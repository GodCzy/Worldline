from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Any

from sqlalchemy import desc, func, select

from src.services.run_queue_service import _redacted_redis_url, get_redis_client
from src.storage.postgres.manager import pg_manager
from src.storage.postgres.models_knowledge import (
    DocumentVersion,
    KnowledgeFile,
    QualityGateRun,
    SourceAsset,
    WorldlineWorkflowRun,
)
from src.utils.datetime_utils import utc_now_naive

FAILED_FILE_STATUSES = {"error_parsing", "error_indexing", "failed", "error"}
PARSING_FAILURE_STATUSES = {"error_parsing", "failed", "error"}
INDEXING_FAILURE_STATUSES = {"error_indexing", "failed", "error"}
ACTIVE_FILE_STATUSES = {"parsing", "indexing", "processing"}
FAILED_RUN_STATUSES = {"failed", "error"}
ACTIVE_RUN_STATUSES = {"planned", "queued", "running", "retrying"}

DEFAULT_OPERATIONAL_BUDGETS = {
    "quality_gate_total_latency_ms": 5000,
    "quality_gate_estimated_usd": 0.10,
    "failed_file_count": 0,
    "failed_workflow_count": 0,
}

RedisHealthProvider = Callable[[], Awaitable[dict[str, Any]]]


class WorldlineOperationalHealthService:
    """Read-only P4 operational readiness report for Worldline jobs and queues."""

    def __init__(
        self,
        *,
        redis_health_provider: RedisHealthProvider | None = None,
        budgets: dict[str, float | int] | None = None,
    ) -> None:
        self.redis_health_provider = redis_health_provider or self._redis_health
        self.budgets = {**DEFAULT_OPERATIONAL_BUDGETS, **(budgets or {})}

    async def build_report(self, *, db_id: str | None = None, limit: int = 10) -> dict[str, Any]:
        limit = max(1, min(int(limit or 10), 50))
        redis_health = await self.redis_health_provider()
        snapshot = await self._collect_snapshot(db_id=db_id, limit=limit)
        budget_report = self._budget_report(snapshot)
        failures = self._failure_evidence(snapshot)
        queues = self._queue_health(snapshot, redis_health)

        status = "healthy"
        if redis_health.get("status") == "unavailable":
            status = "degraded"
        elif (
            failures["summary"]["total_failed_records"] > 0
            or budget_report["violations"]
            or queues["workflow_runs"]["active_count"] > 0
        ):
            status = "attention"

        return {
            "status": status,
            "service": "WorldlineOperationalHealthService",
            "db_id": db_id,
            "generated_at": utc_now_naive().isoformat(),
            "queues": queues,
            "failure_evidence": failures,
            "retry_policy": self._retry_policy(),
            "budgets": budget_report,
            "cleanup_readiness": self._cleanup_readiness(snapshot),
            "next_actions": self._next_actions(status, failures, budget_report),
        }

    async def _collect_snapshot(self, *, db_id: str | None, limit: int) -> dict[str, Any]:
        async with pg_manager.get_async_session_context() as session:
            file_status_rows = await session.execute(
                self._scope(
                    select(KnowledgeFile.status, func.count()).group_by(KnowledgeFile.status),
                    KnowledgeFile,
                    db_id,
                )
            )
            workflow_status_rows = await session.execute(
                self._scope(
                    select(WorldlineWorkflowRun.status, func.count()).group_by(WorldlineWorkflowRun.status),
                    WorldlineWorkflowRun,
                    db_id,
                )
            )
            gate_status_rows = await session.execute(
                self._scope(
                    select(QualityGateRun.status, func.count()).group_by(QualityGateRun.status),
                    QualityGateRun,
                    db_id,
                )
            )
            document_status_rows = await session.execute(
                self._scope(
                    select(DocumentVersion.status, func.count())
                    .join(SourceAsset, DocumentVersion.asset_id == SourceAsset.asset_id)
                    .group_by(DocumentVersion.status),
                    SourceAsset,
                    db_id,
                )
            )

            recent_files = (
                await session.execute(
                    self._scope(
                        select(KnowledgeFile)
                        .where(KnowledgeFile.status.in_(FAILED_FILE_STATUSES))
                        .order_by(desc(KnowledgeFile.updated_at), desc(KnowledgeFile.id))
                        .limit(limit),
                        KnowledgeFile,
                        db_id,
                    )
                )
            ).scalars().all()
            recent_documents = (
                await session.execute(
                    self._scope(
                        select(DocumentVersion, SourceAsset)
                        .join(SourceAsset, DocumentVersion.asset_id == SourceAsset.asset_id)
                        .where(DocumentVersion.status.in_(FAILED_RUN_STATUSES))
                        .order_by(desc(DocumentVersion.updated_at), desc(DocumentVersion.id))
                        .limit(limit),
                        SourceAsset,
                        db_id,
                    )
                )
            ).all()
            recent_workflows = (
                await session.execute(
                    self._scope(
                        select(WorldlineWorkflowRun)
                        .where(WorldlineWorkflowRun.status.in_(FAILED_RUN_STATUSES | ACTIVE_RUN_STATUSES))
                        .order_by(desc(WorldlineWorkflowRun.updated_at), desc(WorldlineWorkflowRun.id))
                        .limit(limit),
                        WorldlineWorkflowRun,
                        db_id,
                    )
                )
            ).scalars().all()
            recent_gates = (
                await session.execute(
                    self._scope(
                        select(QualityGateRun)
                        .where(QualityGateRun.status.in_(FAILED_RUN_STATUSES))
                        .order_by(desc(QualityGateRun.created_at), desc(QualityGateRun.id))
                        .limit(limit),
                        QualityGateRun,
                        db_id,
                    )
                )
            ).scalars().all()
            latest_gate = (
                await session.execute(
                    self._scope(
                        select(QualityGateRun)
                        .order_by(desc(QualityGateRun.created_at), desc(QualityGateRun.id))
                        .limit(1),
                        QualityGateRun,
                        db_id,
                    )
                )
            ).scalar_one_or_none()

        return {
            "file_status_counts": self._counts(file_status_rows.all()),
            "workflow_status_counts": self._counts(workflow_status_rows.all()),
            "gate_status_counts": self._counts(gate_status_rows.all()),
            "document_status_counts": self._counts(document_status_rows.all()),
            "recent_files": [self._serialize_file(row) for row in recent_files],
            "recent_documents": [self._serialize_document(version, asset) for version, asset in recent_documents],
            "recent_workflows": [self._serialize_workflow(row) for row in recent_workflows],
            "recent_gates": [self._serialize_gate(row) for row in recent_gates],
            "latest_gate": self._serialize_gate(latest_gate) if latest_gate else None,
        }

    def _scope(self, stmt, model, db_id: str | None):
        if not db_id:
            return stmt
        return stmt.where(model.db_id == db_id)

    async def _redis_health(self) -> dict[str, Any]:
        try:
            redis = await get_redis_client()
            await redis.ping()
            kwargs = getattr(getattr(redis, "connection_pool", None), "connection_kwargs", {}) or {}
            redis_host = str(kwargs.get("host") or "")
            return {
                "status": "available",
                "backend": "redis",
                "url": _redacted_redis_url(redis_host),
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "unavailable",
                "backend": "redis",
                "error": str(exc),
                "retryable": True,
            }

    def _queue_health(self, snapshot: dict[str, Any], redis_health: dict[str, Any]) -> dict[str, Any]:
        file_counts = snapshot["file_status_counts"]
        workflow_counts = snapshot["workflow_status_counts"]
        return {
            "redis": redis_health,
            "knowledge_files": {
                "by_status": file_counts,
                "failed_count": self._sum_counts(file_counts, FAILED_FILE_STATUSES),
                "active_count": self._sum_counts(file_counts, ACTIVE_FILE_STATUSES),
                "recent_failed": snapshot["recent_files"],
            },
            "workflow_runs": {
                "by_status": workflow_counts,
                "failed_count": self._sum_counts(workflow_counts, FAILED_RUN_STATUSES),
                "active_count": self._sum_counts(workflow_counts, ACTIVE_RUN_STATUSES),
                "recent": snapshot["recent_workflows"],
            },
        }

    def _failure_evidence(self, snapshot: dict[str, Any]) -> dict[str, Any]:
        files = snapshot["recent_files"]
        documents = snapshot["recent_documents"]
        gates = snapshot["recent_gates"]
        workflows = snapshot["recent_workflows"]

        parsing_failures = [row for row in files if row["status"] in PARSING_FAILURE_STATUSES] + documents
        indexing_failures = [row for row in files if row["status"] in INDEXING_FAILURE_STATUSES]
        workflow_failures = [row for row in workflows if row["status"] in FAILED_RUN_STATUSES]
        total_failed_records = len(parsing_failures) + len(indexing_failures) + len(workflow_failures) + len(gates)
        return {
            "summary": {
                "total_failed_records": total_failed_records,
                "document_versions_failed": self._sum_counts(snapshot["document_status_counts"], FAILED_RUN_STATUSES),
                "quality_gates_failed": self._sum_counts(snapshot["gate_status_counts"], FAILED_RUN_STATUSES),
                "workflow_runs_failed": self._sum_counts(snapshot["workflow_status_counts"], FAILED_RUN_STATUSES),
            },
            "parsing": {
                "failed_count": len(parsing_failures),
                "recent": parsing_failures,
            },
            "indexing": {
                "failed_count": len(indexing_failures),
                "recent": indexing_failures,
            },
            "wiki_generation": self._workflow_stage("worldline.rebuild_wiki", workflows),
            "graph_rebuild": self._workflow_stage("worldline.update_graph", workflows),
            "quality_gates": {
                "failed_count": len(gates),
                "recent": gates,
            },
        }

    def _workflow_stage(self, tool_name: str, workflows: list[dict[str, Any]]) -> dict[str, Any]:
        rows = [row for row in workflows if tool_name in row["step_tools"]]
        failed = [row for row in rows if row["status"] in FAILED_RUN_STATUSES]
        return {
            "failed_count": len(failed),
            "active_count": len([row for row in rows if row["status"] in ACTIVE_RUN_STATUSES]),
            "recent": rows,
            "retryable_statuses": sorted(FAILED_RUN_STATUSES),
        }

    def _retry_policy(self) -> dict[str, Any]:
        return {
            "release_gate": "worldline_operational_readiness_contract",
            "stages": {
                "parsing": {
                    "retryable_statuses": sorted(PARSING_FAILURE_STATUSES),
                    "evidence_fields": ["file_id", "status", "error_message", "processing_params"],
                    "next_step": "requeue parse_file through the knowledge service boundary",
                },
                "indexing": {
                    "retryable_statuses": sorted(INDEXING_FAILURE_STATUSES),
                    "evidence_fields": ["file_id", "status", "error_message", "processing_params"],
                    "next_step": "requeue index_file through the knowledge service boundary",
                },
                "wiki_generation": {
                    "retryable_statuses": sorted(FAILED_RUN_STATUSES),
                    "evidence_fields": ["workflow_id", "status", "steps", "trace"],
                    "next_step": "requeue worldline.rebuild_wiki from a workflow run",
                },
                "graph_rebuild": {
                    "retryable_statuses": sorted(FAILED_RUN_STATUSES),
                    "evidence_fields": ["workflow_id", "status", "steps", "trace"],
                    "next_step": "requeue worldline.update_graph from a workflow run",
                },
                "quality_gate": {
                    "retryable_statuses": sorted(FAILED_RUN_STATUSES),
                    "evidence_fields": ["gate_id", "status", "failure_replay", "latency_stats", "cost_stats"],
                    "next_step": "requeue worldline.run_quality_gate from a workflow run",
                },
            },
        }

    def _budget_report(self, snapshot: dict[str, Any]) -> dict[str, Any]:
        latest_gate = snapshot["latest_gate"] or {}
        latency_stats = latest_gate.get("latency_stats") or {}
        cost_stats = latest_gate.get("cost_stats") or {}
        latest_latency = float(latency_stats.get("total_ms") or 0)
        latest_cost = float(cost_stats.get("estimated_usd") or 0)
        failed_files = self._sum_counts(snapshot["file_status_counts"], FAILED_FILE_STATUSES)
        failed_workflows = self._sum_counts(snapshot["workflow_status_counts"], FAILED_RUN_STATUSES)
        observed = {
            "quality_gate_total_latency_ms": latest_latency,
            "quality_gate_estimated_usd": latest_cost,
            "failed_file_count": failed_files,
            "failed_workflow_count": failed_workflows,
        }
        violations = [
            {"metric": metric, "observed": value, "budget": self.budgets[metric]}
            for metric, value in observed.items()
            if value > float(self.budgets[metric])
        ]
        return {
            "defaults": dict(self.budgets),
            "observed": observed,
            "latest_quality_gate": latest_gate,
            "violations": violations,
        }

    def _cleanup_readiness(self, snapshot: dict[str, Any]) -> dict[str, Any]:
        return {
            "temporary_file_cleanup": "tracked_by_knowledge_file_status",
            "deleted_kb_cleanup": "requires_follow_up_cleanup_routine",
            "minio_object_cleanup": "requires_follow_up_cleanup_routine",
            "archived_artifact_cleanup": "requires_follow_up_cleanup_routine",
            "blocked_by_active_workflows": snapshot["workflow_status_counts"].get("running", 0) > 0,
        }

    def _next_actions(
        self,
        status: str,
        failures: dict[str, Any],
        budget_report: dict[str, Any],
    ) -> list[str]:
        actions = []
        if status == "degraded":
            actions.append("restore Redis/ARQ queue availability before dispatching retry jobs")
        if failures["summary"]["total_failed_records"] > 0:
            actions.append("review recent failure evidence and requeue through controlled service APIs")
        if budget_report["violations"]:
            actions.append("lower cost/latency or adjust budgets with recorded justification")
        if not actions:
            actions.append("continue monitoring operational health before public demo")
        return actions

    @staticmethod
    def _counts(rows: list[tuple[Any, int]]) -> dict[str, int]:
        return {str(status or "unknown"): int(count or 0) for status, count in rows}

    @staticmethod
    def _sum_counts(counts: dict[str, int], statuses: set[str]) -> int:
        return sum(int(counts.get(status, 0)) for status in statuses)

    @staticmethod
    def _iso(value: datetime | None) -> str | None:
        return value.isoformat() if value else None

    def _serialize_file(self, row: KnowledgeFile) -> dict[str, Any]:
        return {
            "file_id": row.file_id,
            "db_id": row.db_id,
            "filename": row.filename,
            "status": row.status,
            "error_message": row.error_message,
            "processing_params": row.processing_params or {},
            "updated_at": self._iso(row.updated_at),
        }

    def _serialize_document(self, version: DocumentVersion, asset: SourceAsset) -> dict[str, Any]:
        return {
            "doc_version_id": version.doc_version_id,
            "asset_id": version.asset_id,
            "db_id": asset.db_id,
            "file_id": version.file_id,
            "status": version.status,
            "parser": version.parser,
            "parser_trace": (version.parse_config or {}).get("parser_trace") or [],
            "error_message": version.error_message,
            "updated_at": self._iso(version.updated_at),
        }

    def _serialize_workflow(self, row: WorldlineWorkflowRun) -> dict[str, Any]:
        steps = list(row.steps or [])
        return {
            "workflow_id": row.workflow_id,
            "db_id": row.db_id,
            "workflow_type": row.workflow_type,
            "status": row.status,
            "dispatch_backend": row.dispatch_backend,
            "step_tools": [str(step.get("tool")) for step in steps if isinstance(step, dict)],
            "trace": row.trace or {},
            "updated_at": self._iso(row.updated_at),
        }

    def _serialize_gate(self, row: QualityGateRun) -> dict[str, Any]:
        return {
            "gate_id": row.gate_id,
            "db_id": row.db_id,
            "status": row.status,
            "metrics": row.metrics or {},
            "failure_replay": row.failure_replay or {},
            "cost_stats": row.cost_stats or {},
            "latency_stats": row.latency_stats or {},
            "completed_at": self._iso(row.completed_at),
        }
