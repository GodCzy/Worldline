from __future__ import annotations

from pathlib import Path

import pytest

from src.services.worldline_operational_health_service import WorldlineOperationalHealthService
from src.storage.postgres.manager import pg_manager
from src.storage.postgres.models_knowledge import (
    DocumentVersion,
    KnowledgeBase,
    KnowledgeFile,
    QualityGateRun,
    SourceAsset,
    WorldlineWorkflowRun,
)
from src.utils.datetime_utils import utc_now_naive


@pytest.fixture()
async def sqlite_pg_manager(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    if pg_manager.async_engine is not None:
        await pg_manager.close()
    pg_manager.async_engine = None
    pg_manager.AsyncSession = None
    pg_manager._initialized = False
    monkeypatch.setenv("POSTGRES_URL", f"sqlite+aiosqlite:///{tmp_path / 'worldline.db'}")
    pg_manager.initialize()
    await pg_manager.create_tables()
    try:
        yield pg_manager
    finally:
        await pg_manager.close()
        pg_manager.async_engine = None
        pg_manager.AsyncSession = None
        pg_manager._initialized = False


async def _available_redis() -> dict:
    return {"status": "available", "backend": "redis", "url": "redis"}


async def _unavailable_redis() -> dict:
    return {"status": "unavailable", "backend": "redis", "error": "connection refused", "retryable": True}


@pytest.mark.asyncio
async def test_operational_health_reports_failures_retry_policy_and_budgets(sqlite_pg_manager) -> None:
    now = utc_now_naive()
    async with sqlite_pg_manager.get_async_session_context() as session:
        session.add(KnowledgeBase(db_id="kb_ops", name="Ops KB", kb_type="milvus"))
        session.add(
            KnowledgeFile(
                file_id="file_parse_fail",
                db_id="kb_ops",
                filename="parse.pdf",
                status="error_parsing",
                error_message="parser failed",
                processing_params={"content_type": "file"},
            )
        )
        session.add(
            KnowledgeFile(
                file_id="file_index_fail",
                db_id="kb_ops",
                filename="index.md",
                status="error_indexing",
                error_message="index failed",
                processing_params={"chunk_preset_id": "general"},
            )
        )
        session.add(
            SourceAsset(
                asset_id="asset_parse_fail",
                db_id="kb_ops",
                asset_type="file",
                uri="parse.pdf",
                status="error",
            )
        )
        session.add(
            DocumentVersion(
                doc_version_id="docv_parse_fail",
                asset_id="asset_parse_fail",
                file_id="file_parse_fail",
                parser="docling",
                status="failed",
                parse_config={"parser_trace": [{"parser": "docling", "status": "failed", "error": "bad"}]},
                stats={"parser_failure_count": 1},
                error_message="bad",
            )
        )
        session.add(
            WorldlineWorkflowRun(
                workflow_id="wfr_failed",
                db_id="kb_ops",
                workflow_type="knowledge_refresh",
                status="failed",
                steps=[
                    {"tool": "worldline.rebuild_wiki"},
                    {"tool": "worldline.update_graph"},
                    {"tool": "worldline.run_quality_gate"},
                ],
                trace={"failed_step": "worldline.update_graph"},
            )
        )
        session.add(
            QualityGateRun(
                gate_id="gate_failed",
                db_id="kb_ops",
                status="failed",
                metrics={"evidence_accuracy": 0.4},
                failure_replay={"items": [{"check": "evidence_accuracy"}]},
                cost_stats={"estimated_usd": 0.25},
                latency_stats={"total_ms": 9000},
                completed_at=now,
            )
        )

    report = await WorldlineOperationalHealthService(redis_health_provider=_available_redis).build_report(
        db_id="kb_ops"
    )

    assert report["status"] == "attention"
    assert report["queues"]["redis"]["status"] == "available"
    assert report["queues"]["knowledge_files"]["failed_count"] == 2
    assert report["queues"]["workflow_runs"]["failed_count"] == 1
    assert report["failure_evidence"]["parsing"]["failed_count"] == 2
    assert report["failure_evidence"]["indexing"]["failed_count"] == 1
    assert report["failure_evidence"]["wiki_generation"]["failed_count"] == 1
    assert report["failure_evidence"]["graph_rebuild"]["failed_count"] == 1
    assert report["failure_evidence"]["quality_gates"]["failed_count"] == 1
    assert set(report["retry_policy"]["stages"]) == {
        "parsing",
        "indexing",
        "wiki_generation",
        "graph_rebuild",
        "quality_gate",
    }
    violation_metrics = {item["metric"] for item in report["budgets"]["violations"]}
    assert {
        "quality_gate_total_latency_ms",
        "quality_gate_estimated_usd",
        "failed_file_count",
        "failed_workflow_count",
    } <= violation_metrics
    assert report["cleanup_readiness"]["minio_object_cleanup"] == "requires_follow_up_cleanup_routine"


@pytest.mark.asyncio
async def test_operational_health_marks_redis_unavailable_as_degraded(sqlite_pg_manager) -> None:
    async with sqlite_pg_manager.get_async_session_context() as session:
        session.add(KnowledgeBase(db_id="kb_healthy", name="Healthy KB", kb_type="milvus"))

    report = await WorldlineOperationalHealthService(redis_health_provider=_unavailable_redis).build_report(
        db_id="kb_healthy"
    )

    assert report["status"] == "degraded"
    assert report["queues"]["redis"]["retryable"] is True
    assert report["next_actions"][0].startswith("restore Redis")
