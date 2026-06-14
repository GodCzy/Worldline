from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from sqlalchemy import desc, select

from src.services.worldline_agent_workflow_service import WorldlineAgentWorkflowService
from src.services.worldline_operational_health_service import (
    FAILED_FILE_STATUSES,
    FAILED_RUN_STATUSES,
    INDEXING_FAILURE_STATUSES,
    PARSING_FAILURE_STATUSES,
)
from src.services.worldline_run_ledger_service import WorldlineRunLedgerService
from src.storage.minio.client import MinIOClient, StorageError
from src.storage.postgres.manager import pg_manager
from src.storage.postgres.models_knowledge import (
    DocumentVersion,
    KnowledgeBase,
    KnowledgeFile,
    QualityGateRun,
    SourceAsset,
    WikiPage,
    WorldlineWorkflowRun,
)
from src.utils import hashstr
from src.utils.datetime_utils import utc_now_naive

REQUEUE_STAGE_TO_TOOL = {
    "parsing": "worldline.compile_document",
    "indexing": "worldline.compile_document",
    "wiki_generation": "worldline.rebuild_wiki",
    "graph_rebuild": "worldline.update_graph",
    "quality_gate": "worldline.run_quality_gate",
}

DEFAULT_BUDGET_SCOPES = {
    "kb": {
        "failed_file_count": 0,
        "failed_workflow_count": 0,
        "active_workflow_count": 2,
    },
    "run": {
        "total_latency_ms": 600000,
        "estimated_usd": 1.0,
    },
    "branch": {
        "generation_latency_ms": 15000,
        "estimated_usd": 0.10,
    },
    "gate": {
        "total_latency_ms": 5000,
        "estimated_usd": 0.10,
    },
}


class WorldlineOperationalActionService:
    """Controlled P4 operational write actions.

    The read-only health report stays in `WorldlineOperationalHealthService`.
    This service only mutates existing operational metadata and always records
    an audit log through the Worldline service boundary.
    """

    def __init__(
        self,
        *,
        audit_service: WorldlineAgentWorkflowService | None = None,
        run_ledger_service: WorldlineRunLedgerService | None = None,
        minio_client: MinIOClient | None = None,
    ) -> None:
        self.audit_service = audit_service or WorldlineAgentWorkflowService()
        self.run_ledger_service = run_ledger_service or WorldlineRunLedgerService()
        self.minio_client = minio_client

    async def run_action(
        self,
        db_id: str,
        *,
        action: str,
        payload: dict[str, Any] | None = None,
        actor: str = "system",
    ) -> dict[str, Any]:
        normalized = str(action or "").strip().lower().replace("-", "_")
        payload = payload or {}
        if normalized == "requeue":
            return await self.requeue_failed(db_id, payload=payload, actor=actor)
        if normalized == "mark_source_stale":
            return await self.mark_source_stale(db_id, payload=payload, actor=actor)
        if normalized == "update_budgets":
            return await self.update_budgets(db_id, payload=payload, actor=actor)
        if normalized == "cleanup":
            return await self.cleanup(db_id, payload=payload, actor=actor)
        raise ValueError(f"Unsupported Worldline operational action: {action}")

    async def requeue_failed(
        self,
        db_id: str,
        *,
        payload: dict[str, Any] | None = None,
        actor: str = "system",
    ) -> dict[str, Any]:
        payload = payload or {}
        stages = self._normalize_stages(payload.get("stages"))
        limit = self._limit(payload.get("limit"), default=20, maximum=100)
        dry_run = bool(payload.get("dry_run") or payload.get("dryRun"))
        operation_id = self._operation_id(db_id, "requeue")
        now = utc_now_naive()
        operation_entry = self._operation_entry(
            operation_id,
            "requeue",
            actor=actor,
            dry_run=dry_run,
            requested={"stages": stages, "limit": limit},
        )

        result: dict[str, Any] = {
            "operation_id": operation_id,
            "action": "requeue",
            "db_id": db_id,
            "status": "dry_run" if dry_run else "queued",
            "dry_run": dry_run,
            "stages": stages,
            "candidates": {},
            "workflow_ids": [],
        }

        selected_tools = [REQUEUE_STAGE_TO_TOOL[stage] for stage in stages]
        async with pg_manager.get_async_session_context() as session:
            if "parsing" in stages or "indexing" in stages:
                file_statuses = set()
                if "parsing" in stages:
                    file_statuses.update(PARSING_FAILURE_STATUSES)
                if "indexing" in stages:
                    file_statuses.update(INDEXING_FAILURE_STATUSES)
                files = (
                    await session.execute(
                        select(KnowledgeFile)
                        .where(KnowledgeFile.db_id == db_id, KnowledgeFile.status.in_(file_statuses))
                        .order_by(desc(KnowledgeFile.updated_at), desc(KnowledgeFile.id))
                        .limit(limit)
                    )
                ).scalars().all()
                documents = (
                    await session.execute(
                        select(DocumentVersion, SourceAsset)
                        .join(SourceAsset, DocumentVersion.asset_id == SourceAsset.asset_id)
                        .where(SourceAsset.db_id == db_id, DocumentVersion.status.in_(FAILED_RUN_STATUSES))
                        .order_by(desc(DocumentVersion.updated_at), desc(DocumentVersion.id))
                        .limit(limit)
                    )
                ).all()
                result["candidates"]["files"] = [self._file_candidate(row) for row in files]
                result["candidates"]["documents"] = [
                    self._document_candidate(version, asset) for version, asset in documents
                ]
                if not dry_run:
                    for row in files:
                        previous_status = row.status
                        row.status = "queued"
                        row.error_message = row.error_message
                        row.updated_by = actor
                        row.updated_at = now
                        row.processing_params = self._append_operation(
                            row.processing_params,
                            operation_entry | {"previous_status": previous_status},
                        )
                    for version, _asset in documents:
                        previous_status = version.status
                        version.status = "retrying"
                        version.updated_at = now
                        version.parse_config = self._append_operation(
                            version.parse_config,
                            operation_entry | {"previous_status": previous_status},
                        )

            workflow_stages = {"wiki_generation", "graph_rebuild", "quality_gate"} & set(stages)
            if workflow_stages:
                workflows = (
                    await session.execute(
                        select(WorldlineWorkflowRun)
                        .where(
                            WorldlineWorkflowRun.db_id == db_id,
                            WorldlineWorkflowRun.status.in_(FAILED_RUN_STATUSES),
                        )
                        .order_by(desc(WorldlineWorkflowRun.updated_at), desc(WorldlineWorkflowRun.id))
                        .limit(limit)
                    )
                ).scalars().all()
                gates = (
                    await session.execute(
                        select(QualityGateRun)
                        .where(QualityGateRun.db_id == db_id, QualityGateRun.status.in_(FAILED_RUN_STATUSES))
                        .order_by(desc(QualityGateRun.created_at), desc(QualityGateRun.id))
                        .limit(limit)
                    )
                ).scalars().all()
                result["candidates"]["workflows"] = [self._workflow_candidate(row) for row in workflows]
                result["candidates"]["quality_gates"] = [self._gate_candidate(row) for row in gates]
                if not dry_run:
                    for row in workflows:
                        previous_status = row.status
                        row.status = "queued"
                        row.updated_at = now
                        row.trace = self._append_operation(
                            row.trace,
                            operation_entry | {"previous_status": previous_status},
                        )

            if not dry_run and selected_tools:
                workflow_id = self._insert_workflow_run(
                    session,
                    db_id=db_id,
                    workflow_type="operational_requeue",
                    tools=selected_tools,
                    actor=actor,
                    operation_id=operation_id,
                    reason=str(payload.get("reason") or "P4 controlled requeue"),
                )
                result["workflow_ids"].append(workflow_id)

        result["candidate_count"] = sum(len(items) for items in result["candidates"].values())
        if not dry_run and result["candidate_count"] == 0:
            result["status"] = "noop"
        result["audit"] = await self._audit(db_id, "worldline.operational_requeue", actor, payload, result)
        return result

    async def mark_source_stale(
        self,
        db_id: str,
        *,
        payload: dict[str, Any] | None = None,
        actor: str = "system",
    ) -> dict[str, Any]:
        payload = payload or {}
        operation_id = self._operation_id(db_id, "mark_source_stale")
        now = utc_now_naive()
        asset_id = str(payload.get("asset_id") or payload.get("assetId") or "").strip()
        file_id = str(payload.get("file_id") or payload.get("fileId") or "").strip()
        source_uri = str(payload.get("source_uri") or payload.get("sourceUri") or "").strip()
        new_hash = str(payload.get("content_hash") or payload.get("contentHash") or "").strip()
        reason = str(payload.get("reason") or "source version changed").strip()
        dry_run = bool(payload.get("dry_run") or payload.get("dryRun"))

        if not any((asset_id, file_id, source_uri)):
            raise ValueError("asset_id, file_id, or source_uri is required")

        result: dict[str, Any] = {
            "operation_id": operation_id,
            "action": "mark_source_stale",
            "db_id": db_id,
            "status": "dry_run" if dry_run else "queued",
            "dry_run": dry_run,
            "asset": None,
            "stale_pages": [],
            "workflow_ids": [],
        }

        async with pg_manager.get_async_session_context() as session:
            stmt = select(SourceAsset).where(SourceAsset.db_id == db_id)
            if asset_id:
                stmt = stmt.where(SourceAsset.asset_id == asset_id)
            elif file_id:
                stmt = stmt.where(SourceAsset.asset_metadata["file_id"].as_string() == file_id)
            else:
                stmt = stmt.where(SourceAsset.uri == source_uri)
            asset = (await session.execute(stmt.limit(1))).scalar_one_or_none()
            if asset is None:
                raise ValueError("SourceAsset not found for stale marking")

            previous_hash = asset.content_hash
            result["asset"] = {
                "asset_id": asset.asset_id,
                "file_id": (asset.asset_metadata or {}).get("file_id"),
                "source_uri": asset.uri,
                "previous_content_hash": previous_hash,
                "new_content_hash": new_hash or previous_hash,
            }

            page_source_ids = {asset.asset_id, asset.uri}
            if (asset.asset_metadata or {}).get("file_id"):
                page_source_ids.add(str((asset.asset_metadata or {}).get("file_id")))
            pages = (
                await session.execute(
                    select(WikiPage)
                    .where(WikiPage.db_id == db_id, WikiPage.source_id.in_(page_source_ids))
                    .order_by(WikiPage.updated_at, WikiPage.id)
                )
            ).scalars().all()
            result["stale_pages"] = [
                {"page_id": page.page_id, "title": page.title, "source_id": page.source_id} for page in pages
            ]

            if not dry_run:
                asset.status = "stale"
                asset.content_hash = new_hash or asset.content_hash
                asset.updated_at = now
                asset.asset_metadata = {
                    **(asset.asset_metadata or {}),
                    "worldline_stale": {
                        "operation_id": operation_id,
                        "actor": actor,
                        "marked_at": now.isoformat(),
                        "reason": reason,
                        "previous_content_hash": previous_hash,
                        "new_content_hash": new_hash or previous_hash,
                        "review_state": "stale_review_required",
                    },
                }
                for page in pages:
                    page.status = "stale_review"
                    page.updated_at = now
                    page.freshness = {
                        **(page.freshness or {}),
                        "status": "stale",
                        "review_state": "stale_review_required",
                        "stale_reasons": sorted(
                            set([*(page.freshness or {}).get("stale_reasons", []), "source_version_changed"])
                        ),
                        "operation_id": operation_id,
                        "marked_at": now.isoformat(),
                    }
                workflow_id = self._insert_workflow_run(
                    session,
                    db_id=db_id,
                    workflow_type="stale_source_rebuild",
                    tools=[
                        "worldline.rebuild_wiki",
                        "worldline.update_graph",
                        "worldline.run_quality_gate",
                    ],
                    actor=actor,
                    operation_id=operation_id,
                    reason=reason,
                )
                result["workflow_ids"].append(workflow_id)

        result["audit"] = await self._audit(db_id, "worldline.mark_source_stale", actor, payload, result)
        return result

    async def update_budgets(
        self,
        db_id: str,
        *,
        payload: dict[str, Any] | None = None,
        actor: str = "system",
    ) -> dict[str, Any]:
        payload = payload or {}
        operation_id = self._operation_id(db_id, "update_budgets")
        budgets = self._normalize_budget_payload(payload.get("budgets") or payload)
        now = utc_now_naive()

        async with pg_manager.get_async_session_context() as session:
            kb = (await session.execute(select(KnowledgeBase).where(KnowledgeBase.db_id == db_id))).scalar_one_or_none()
            if kb is None:
                raise ValueError(f"KnowledgeBase {db_id} not found")
            additional = dict(kb.additional_params or {})
            worldline_ops = dict(additional.get("worldline_operational") or {})
            worldline_ops["budgets"] = budgets
            worldline_ops["budget_updated_at"] = now.isoformat()
            worldline_ops["budget_updated_by"] = actor
            additional["worldline_operational"] = worldline_ops
            kb.additional_params = additional
            kb.updated_at = now

        result = {
            "operation_id": operation_id,
            "action": "update_budgets",
            "db_id": db_id,
            "status": "saved",
            "budgets": budgets,
            "updated_at": now.isoformat(),
        }
        result["audit"] = await self._audit(db_id, "worldline.update_operational_budgets", actor, payload, result)
        return result

    async def cleanup(
        self,
        db_id: str,
        *,
        payload: dict[str, Any] | None = None,
        actor: str = "system",
    ) -> dict[str, Any]:
        payload = payload or {}
        operation_id = self._operation_id(db_id, "cleanup")
        targets = self._normalize_cleanup_targets(payload.get("targets"))
        limit = self._limit(payload.get("limit"), default=20, maximum=100)
        dry_run = bool(payload.get("dry_run", payload.get("dryRun", True)))
        delete_minio = bool(payload.get("delete_minio") or payload.get("deleteMinio"))
        prune_archived_artifacts = bool(
            payload.get("prune_archived_artifacts") or payload.get("pruneArchivedArtifacts")
        )
        now = utc_now_naive()
        result: dict[str, Any] = {
            "operation_id": operation_id,
            "action": "cleanup",
            "db_id": db_id,
            "status": "dry_run" if dry_run else "completed",
            "dry_run": dry_run,
            "targets": targets,
            "temporary_files": [],
            "minio_objects": [],
            "deleted_kbs": [],
            "archived_artifacts": {},
        }

        async with pg_manager.get_async_session_context() as session:
            if "temporary_files" in targets:
                files = (
                    await session.execute(
                        select(KnowledgeFile)
                        .where(KnowledgeFile.db_id == db_id, KnowledgeFile.status.in_(FAILED_FILE_STATUSES))
                        .order_by(desc(KnowledgeFile.updated_at), desc(KnowledgeFile.id))
                        .limit(limit)
                    )
                ).scalars().all()
                for row in files:
                    cleanup_record = self._cleanup_file_candidate(row, operation_id=operation_id, dry_run=dry_run)
                    result["temporary_files"].append(cleanup_record)
                    if not dry_run and cleanup_record["status"] in {"removed", "missing", "skipped_no_path"}:
                        row.processing_params = self._append_operation(
                            row.processing_params,
                            {
                                "operation_id": operation_id,
                                "action": "cleanup_temporary_file",
                                "actor": actor,
                                "status": cleanup_record["status"],
                                "path": cleanup_record.get("path"),
                                "requested_at": now.isoformat(),
                            },
                        )
                        row.updated_by = actor
                        row.updated_at = now

            if "minio_objects" in targets:
                rows = (
                    await session.execute(
                        select(KnowledgeFile)
                        .where(KnowledgeFile.db_id == db_id, KnowledgeFile.minio_url.is_not(None))
                        .order_by(desc(KnowledgeFile.updated_at), desc(KnowledgeFile.id))
                        .limit(limit)
                    )
                ).scalars().all()
                for row in rows:
                    cleanup_record = await self._cleanup_minio_candidate(
                        row,
                        dry_run=dry_run,
                        delete_minio=delete_minio,
                    )
                    result["minio_objects"].append(cleanup_record)
                    if not dry_run:
                        row.processing_params = self._append_operation(
                            row.processing_params,
                            {
                                "operation_id": operation_id,
                                "action": "cleanup_minio_object",
                                "actor": actor,
                                "status": cleanup_record["status"],
                                "requested_at": now.isoformat(),
                            },
                        )
                        row.updated_by = actor
                        row.updated_at = now

            if "deleted_kbs" in targets:
                kb = (
                    await session.execute(select(KnowledgeBase).where(KnowledgeBase.db_id == db_id))
                ).scalar_one_or_none()
                readiness = {
                    "db_id": db_id,
                    "status": "ready" if kb and self._kb_marked_deleted(kb) else "requires_deleted_marker",
                    "destructive_delete": False,
                }
                result["deleted_kbs"].append(readiness)

        if "archived_artifacts" in targets:
            result["archived_artifacts"] = await self.run_ledger_service.cleanup_archived_artifacts(
                dry_run=dry_run,
                prune=prune_archived_artifacts,
                actor=actor,
                limit=limit,
            )

        result["audit"] = await self._audit(db_id, "worldline.operational_cleanup", actor, payload, result)
        return result

    def _normalize_stages(self, stages: Any) -> list[str]:
        if not stages:
            return list(REQUEUE_STAGE_TO_TOOL)
        values = stages if isinstance(stages, list) else [stages]
        normalized = []
        for value in values:
            stage = str(value or "").strip().lower().replace("-", "_")
            if stage not in REQUEUE_STAGE_TO_TOOL:
                raise ValueError(f"Unsupported requeue stage: {value}")
            if stage not in normalized:
                normalized.append(stage)
        return normalized

    def _normalize_cleanup_targets(self, targets: Any) -> list[str]:
        allowed = {"temporary_files", "deleted_kbs", "minio_objects", "archived_artifacts"}
        if not targets:
            return sorted(allowed)
        values = targets if isinstance(targets, list) else [targets]
        normalized = []
        for value in values:
            target = str(value or "").strip().lower().replace("-", "_")
            if target not in allowed:
                raise ValueError(f"Unsupported cleanup target: {value}")
            if target not in normalized:
                normalized.append(target)
        return normalized

    def _normalize_budget_payload(self, value: Any) -> dict[str, dict[str, float]]:
        source = value if isinstance(value, dict) else {}
        scoped = source.get("scopes") if isinstance(source.get("scopes"), dict) else source
        result = {scope: dict(defaults) for scope, defaults in DEFAULT_BUDGET_SCOPES.items()}
        for scope, defaults in DEFAULT_BUDGET_SCOPES.items():
            updates = scoped.get(scope) if isinstance(scoped.get(scope), dict) else {}
            for key, default_value in defaults.items():
                if key not in updates:
                    continue
                result[scope][key] = max(0.0, float(updates[key]))
        flat_aliases = {
            "quality_gate_total_latency_ms": ("gate", "total_latency_ms"),
            "quality_gate_estimated_usd": ("gate", "estimated_usd"),
            "failed_file_count": ("kb", "failed_file_count"),
            "failed_workflow_count": ("kb", "failed_workflow_count"),
        }
        for key, (scope, metric) in flat_aliases.items():
            if key in source:
                result[scope][metric] = max(0.0, float(source[key]))
        return result

    @staticmethod
    def _limit(value: Any, *, default: int, maximum: int) -> int:
        try:
            return max(1, min(int(value or default), maximum))
        except Exception:
            return default

    def _insert_workflow_run(
        self,
        session,
        *,
        db_id: str,
        workflow_type: str,
        tools: list[str],
        actor: str,
        operation_id: str,
        reason: str,
    ) -> str:
        unique_tools = []
        for tool in tools:
            if tool not in unique_tools:
                unique_tools.append(tool)
        workflow_id = f"wfr_{hashstr(f'{db_id}:{workflow_type}:{operation_id}:{unique_tools}', length=32)}"
        steps = [
            {
                "node_id": f"n{index}_{tool.rsplit('.', 1)[-1]}",
                "tool": tool,
                "dispatch_backend": "arq",
                "write_scope": self._tool_write_scope(tool),
                "requires_admin": True,
                "arq_task_type": tool.replace("worldline.", "worldline:"),
                "operation_id": operation_id,
            }
            for index, tool in enumerate(unique_tools)
        ]
        session.add(
            WorldlineWorkflowRun(
                workflow_id=workflow_id,
                db_id=db_id,
                workflow_type=workflow_type,
                status="queued",
                orchestrator="langgraph",
                dispatch_backend="arq",
                steps=steps,
                trace={
                    "operation_id": operation_id,
                    "policy": "controlled_p4_operational_action",
                    "reason": reason,
                    "queued_at": utc_now_naive().isoformat(),
                },
                created_by=actor,
            )
        )
        return workflow_id

    @staticmethod
    def _tool_write_scope(tool: str) -> str:
        return {
            "worldline.compile_document": "knowledge_objects",
            "worldline.rebuild_wiki": "wiki_pages",
            "worldline.update_graph": "knowledge_graph",
            "worldline.run_quality_gate": "quality_gate_runs",
        }.get(tool, "worldline_operational")

    def _cleanup_file_candidate(self, row: KnowledgeFile, *, operation_id: str, dry_run: bool) -> dict[str, Any]:
        params = row.processing_params or {}
        candidate_path = params.get("temp_path") or params.get("temporary_path") or params.get("local_temp_path") or ""
        if not candidate_path:
            return {"file_id": row.file_id, "status": "skipped_no_path", "path": ""}
        path = Path(str(candidate_path)).expanduser()
        is_safe = self._is_safe_temp_path(path)
        record = {"file_id": row.file_id, "path": str(path), "safe": is_safe, "status": "would_remove"}
        if not is_safe:
            record["status"] = "blocked_unsafe_path"
            return record
        if dry_run:
            return record
        if not path.exists():
            record["status"] = "missing"
            return record
        if path.is_file():
            path.unlink()
            record["status"] = "removed"
            return record
        record["status"] = "blocked_not_file"
        return record

    async def _cleanup_minio_candidate(
        self,
        row: KnowledgeFile,
        *,
        dry_run: bool,
        delete_minio: bool,
    ) -> dict[str, Any]:
        bucket, object_name = self._parse_minio_url(row.minio_url or "")
        record = {
            "file_id": row.file_id,
            "minio_url": row.minio_url,
            "bucket": bucket,
            "object_name": object_name,
            "status": "would_delete" if bucket and object_name else "skipped_unparseable_url",
        }
        if not bucket or not object_name or dry_run:
            return record
        if not delete_minio:
            record["status"] = "skipped_requires_delete_minio"
            return record
        try:
            client = self.minio_client or MinIOClient()
            deleted = await client.adelete_file(bucket, object_name)
            record["status"] = "deleted" if deleted else "missing"
        except (StorageError, Exception) as exc:  # noqa: BLE001
            record["status"] = "failed"
            record["error"] = str(exc)
        return record

    @staticmethod
    def _parse_minio_url(url: str) -> tuple[str, str]:
        parsed = urlparse(url or "")
        path = parsed.path.strip("/")
        if not path or "/" not in path:
            return "", ""
        bucket, object_name = path.split("/", 1)
        return bucket, object_name

    @staticmethod
    def _is_safe_temp_path(path: Path) -> bool:
        try:
            resolved = path.resolve()
        except Exception:
            return False
        roots = [Path(tempfile.gettempdir()).resolve()]
        return any(resolved == root or root in resolved.parents for root in roots)

    @staticmethod
    def _kb_marked_deleted(kb: KnowledgeBase) -> bool:
        additional = kb.additional_params or {}
        worldline_ops = additional.get("worldline_operational") if isinstance(additional, dict) else {}
        return bool(isinstance(worldline_ops, dict) and worldline_ops.get("deleted_at"))

    @staticmethod
    def _append_operation(payload: Any, entry: dict[str, Any]) -> dict[str, Any]:
        data = dict(payload or {}) if isinstance(payload, dict) else {}
        history = list(data.get("worldline_operations") or [])
        data["worldline_operations"] = [entry, *history[:19]]
        return data

    @staticmethod
    def _operation_entry(
        operation_id: str,
        action: str,
        *,
        actor: str,
        dry_run: bool,
        requested: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "operation_id": operation_id,
            "action": action,
            "actor": actor,
            "dry_run": dry_run,
            "requested": requested,
            "requested_at": utc_now_naive().isoformat(),
        }

    @staticmethod
    def _operation_id(db_id: str, action: str) -> str:
        return f"ops_{hashstr(f'{db_id}:{action}:{utc_now_naive().isoformat()}', length=24)}"

    async def _audit(
        self,
        db_id: str,
        tool_name: str,
        actor: str,
        request_summary: dict[str, Any],
        result_summary: dict[str, Any],
    ) -> dict[str, Any]:
        log = await self.audit_service.audit_tool_call(
            db_id,
            tool_name=tool_name,
            actor=actor,
            status=str(result_summary.get("status") or "success"),
            request_summary=request_summary,
            result_summary={
                "operation_id": result_summary.get("operation_id"),
                "status": result_summary.get("status"),
                "candidate_count": result_summary.get("candidate_count"),
                "workflow_ids": result_summary.get("workflow_ids") or [],
            },
            metadata={"source": "WorldlineOperationalActionService"},
        )
        return {"recorded": True, "log_id": log.get("log_id")}

    @staticmethod
    def _file_candidate(row: KnowledgeFile) -> dict[str, Any]:
        return {
            "file_id": row.file_id,
            "filename": row.filename,
            "status": row.status,
            "error_message": row.error_message,
        }

    @staticmethod
    def _document_candidate(version: DocumentVersion, asset: SourceAsset) -> dict[str, Any]:
        return {
            "doc_version_id": version.doc_version_id,
            "asset_id": version.asset_id,
            "file_id": version.file_id,
            "source_uri": asset.uri,
            "status": version.status,
            "error_message": version.error_message,
        }

    @staticmethod
    def _workflow_candidate(row: WorldlineWorkflowRun) -> dict[str, Any]:
        return {
            "workflow_id": row.workflow_id,
            "workflow_type": row.workflow_type,
            "status": row.status,
            "step_tools": [str(step.get("tool")) for step in (row.steps or []) if isinstance(step, dict)],
        }

    @staticmethod
    def _gate_candidate(row: QualityGateRun) -> dict[str, Any]:
        return {
            "gate_id": row.gate_id,
            "status": row.status,
            "failure_replay": row.failure_replay or {},
        }
