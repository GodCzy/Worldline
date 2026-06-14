from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import select

from src.services.worldline_operational_action_service import WorldlineOperationalActionService
from src.services.worldline_operational_health_service import WorldlineOperationalHealthService
from src.services.worldline_run_ledger_service import WorldlineRunLedgerService
from src.storage.postgres.manager import pg_manager
from src.storage.postgres.models_knowledge import (
    DocumentVersion,
    KnowledgeBase,
    KnowledgeFile,
    QualityGateRun,
    SourceAsset,
    WikiPage,
    WorldlineMcpAuditLog,
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
    assert report["cleanup_readiness"]["minio_object_cleanup"] == "controlled_routine_available"
    assert report["operation_controls"]["actions"]["requeue"]["dry_run_supported"] is True
    assert "gate" in report["budgets"]["scopes"]["effective"]


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


@pytest.mark.asyncio
async def test_operational_actions_requeue_stale_budget_and_cleanup(
    sqlite_pg_manager,
    tmp_path: Path,
) -> None:
    now = utc_now_naive()
    temp_file = tmp_path / "worldline-temp-download.md"
    temp_file.write_text("temporary compiler artifact", encoding="utf-8")
    ledger_service = WorldlineRunLedgerService(storage_path=tmp_path / "runs.json")
    run = await ledger_service.create_run(
        {
            "id": "run_archived_ops",
            "title": "Archived Ops Run",
            "artifacts": [{"id": "artifact-1", "label": "Replay", "content": {"ok": True}}],
        },
        created_by="ops-test",
    )
    await ledger_service.archive_run(run["id"], {"reason": "cleanup"}, actor="ops-test")

    async with sqlite_pg_manager.get_async_session_context() as session:
        session.add(KnowledgeBase(db_id="kb_ops_actions", name="Ops Actions KB", kb_type="milvus"))
        session.add(
            KnowledgeFile(
                file_id="file_parse_retry",
                db_id="kb_ops_actions",
                filename="parse.pdf",
                status="error_parsing",
                error_message="parser failed",
                processing_params={"content_type": "file"},
            )
        )
        session.add(
            KnowledgeFile(
                file_id="file_temp_cleanup",
                db_id="kb_ops_actions",
                filename="temp.md",
                status="error_indexing",
                error_message="temporary file left",
                processing_params={"temp_path": str(temp_file)},
            )
        )
        session.add(
            KnowledgeFile(
                file_id="file_minio_cleanup",
                db_id="kb_ops_actions",
                filename="minio.pdf",
                status="failed",
                minio_url="http://localhost:9000/kb-documents/kb_ops_actions/minio.pdf",
                processing_params={},
            )
        )
        session.add(
            SourceAsset(
                asset_id="asset_retry",
                db_id="kb_ops_actions",
                asset_type="file",
                uri="parse.pdf",
                status="active",
                content_hash="hash-old",
                asset_metadata={"file_id": "file_parse_retry"},
            )
        )
        session.add(
            DocumentVersion(
                doc_version_id="docv_retry",
                asset_id="asset_retry",
                file_id="file_parse_retry",
                parser="docling",
                status="failed",
                content_hash="hash-old",
                version_index=1,
                parse_config={},
                error_message="parse failed",
            )
        )
        session.add(
            WikiPage(
                page_id="wiki_retry",
                db_id="kb_ops_actions",
                page_type="document",
                slug="retry",
                title="Retry Source",
                source_id="file_parse_retry",
                markdown="# Retry",
                freshness={"status": "fresh", "source_doc_version_ids": ["docv_retry"]},
                status="active",
            )
        )
        session.add(
            WorldlineWorkflowRun(
                workflow_id="wfr_retry_failed",
                db_id="kb_ops_actions",
                workflow_type="knowledge_refresh",
                status="failed",
                steps=[{"tool": "worldline.rebuild_wiki"}, {"tool": "worldline.run_quality_gate"}],
                trace={"failed_step": "worldline.rebuild_wiki"},
            )
        )
        session.add(
            QualityGateRun(
                gate_id="gate_retry_failed",
                db_id="kb_ops_actions",
                status="failed",
                metrics={"evidence_accuracy": 0.5},
                failure_replay={"items": [{"check": "evidence_accuracy"}]},
                cost_stats={"estimated_usd": 0.25},
                latency_stats={"total_ms": 9000},
                completed_at=now,
            )
        )

    service = WorldlineOperationalActionService(run_ledger_service=ledger_service)
    requeue = await service.requeue_failed(
        "kb_ops_actions",
        payload={"stages": ["parsing", "wiki_generation", "quality_gate"], "limit": 10},
        actor="ops-admin",
    )
    assert requeue["status"] == "queued"
    assert requeue["candidate_count"] >= 3
    assert requeue["workflow_ids"]

    stale = await service.mark_source_stale(
        "kb_ops_actions",
        payload={"file_id": "file_parse_retry", "content_hash": "hash-new"},
        actor="ops-admin",
    )
    assert stale["status"] == "queued"
    assert stale["workflow_ids"]
    assert stale["stale_pages"][0]["page_id"] == "wiki_retry"

    budget = await service.update_budgets(
        "kb_ops_actions",
        payload={"budgets": {"gate": {"total_latency_ms": 1, "estimated_usd": 0.01}}},
        actor="ops-admin",
    )
    assert budget["budgets"]["gate"]["total_latency_ms"] == 1

    cleanup = await service.cleanup(
        "kb_ops_actions",
        payload={
            "targets": ["temporary_files", "minio_objects", "archived_artifacts"],
            "dry_run": False,
            "delete_minio": False,
            "prune_archived_artifacts": True,
            "limit": 20,
        },
        actor="ops-admin",
    )
    assert cleanup["status"] == "completed"
    assert not temp_file.exists()
    assert any(item["status"] == "skipped_requires_delete_minio" for item in cleanup["minio_objects"])
    assert cleanup["archived_artifacts"]["pruned_count"] == 1

    report = await WorldlineOperationalHealthService(redis_health_provider=_available_redis).build_report(
        db_id="kb_ops_actions"
    )
    gate_violations = {
        (item["scope"], item["metric"]) for item in report["budgets"]["scopes"]["violations"]
    }
    assert ("gate", "total_latency_ms") in gate_violations
    assert report["cleanup_readiness"]["archived_artifact_cleanup"] == "controlled_routine_available"

    async with sqlite_pg_manager.get_async_session_context() as session:
        file_row = (
            await session.execute(select(KnowledgeFile).where(KnowledgeFile.file_id == "file_parse_retry"))
        ).scalar_one()
        doc_row = (
            await session.execute(select(DocumentVersion).where(DocumentVersion.doc_version_id == "docv_retry"))
        ).scalar_one()
        asset_row = (
            await session.execute(select(SourceAsset).where(SourceAsset.asset_id == "asset_retry"))
        ).scalar_one()
        page_row = (await session.execute(select(WikiPage).where(WikiPage.page_id == "wiki_retry"))).scalar_one()
        audit_count = (
            await session.execute(
                select(WorldlineMcpAuditLog).where(WorldlineMcpAuditLog.db_id == "kb_ops_actions")
            )
        ).scalars().all()

    assert file_row.status == "queued"
    assert doc_row.status == "retrying"
    assert asset_row.status == "stale"
    assert page_row.status == "stale_review"
    assert len(audit_count) >= 4
