from __future__ import annotations

from typing import Any

from sqlalchemy import delete, select

from src.storage.postgres.manager import pg_manager
from src.storage.postgres.models_knowledge import (
    GoldenSetItem,
    KnowledgeChunk,
    KnowledgeEntity,
    KnowledgeFile,
    KnowledgeRelationship,
    QualityGateRun,
    TemporalFact,
    WikiPage,
    WorldlineMcpAuditLog,
    WorldlineWorkflowRun,
)


class KnowledgeGraphRepository:
    """Persistence boundary for local graph, temporal, workflow, and gate artifacts."""

    async def list_source_chunks(self, db_id: str) -> list[dict[str, Any]]:
        async with pg_manager.get_async_session_context() as session:
            stmt = (
                select(KnowledgeChunk, KnowledgeFile)
                .join(KnowledgeFile, KnowledgeChunk.file_id == KnowledgeFile.file_id)
                .where(KnowledgeChunk.db_id == db_id)
                .order_by(KnowledgeFile.filename, KnowledgeChunk.chunk_index)
            )
            rows = (await session.execute(stmt)).all()

        return [
            {
                "chunk_id": chunk.chunk_id,
                "db_id": chunk.db_id,
                "file_id": chunk.file_id,
                "filename": file_record.filename,
                "doc_version_id": chunk.doc_version_id,
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
                "evidence_ids": list(chunk.evidence_ids or []),
                "metadata": chunk.chunk_metadata or {},
            }
            for chunk, file_record in rows
        ]

    async def replace_graph(self, db_id: str) -> None:
        async with pg_manager.get_async_session_context() as session:
            await session.execute(delete(TemporalFact).where(TemporalFact.db_id == db_id))
            await session.execute(delete(KnowledgeRelationship).where(KnowledgeRelationship.db_id == db_id))
            await session.execute(delete(KnowledgeEntity).where(KnowledgeEntity.db_id == db_id))

    async def insert_entities(self, entities: list[dict[str, Any]]) -> None:
        if not entities:
            return
        async with pg_manager.get_async_session_context() as session:
            for entity in entities:
                session.add(KnowledgeEntity(**entity))

    async def insert_relationships(self, relationships: list[dict[str, Any]]) -> None:
        if not relationships:
            return
        async with pg_manager.get_async_session_context() as session:
            for relationship in relationships:
                session.add(KnowledgeRelationship(**relationship))

    async def insert_temporal_facts(self, facts: list[dict[str, Any]]) -> None:
        if not facts:
            return
        async with pg_manager.get_async_session_context() as session:
            for fact in facts:
                session.add(TemporalFact(**fact))

    async def list_entities(self, db_id: str, *, limit: int = 100, offset: int = 0) -> dict[str, Any]:
        limit = max(1, min(int(limit or 100), 500))
        offset = max(0, int(offset or 0))
        async with pg_manager.get_async_session_context() as session:
            rows = (
                await session.execute(
                    select(KnowledgeEntity)
                    .where(KnowledgeEntity.db_id == db_id)
                    .order_by(KnowledgeEntity.name)
                    .offset(offset)
                    .limit(limit + 1)
                )
            ).scalars().all()
        return {
            "items": [self.serialize_entity(row) for row in rows[:limit]],
            "limit": limit,
            "offset": offset,
            "has_more": len(rows) > limit,
        }

    async def list_relationships(self, db_id: str, *, limit: int = 100, offset: int = 0) -> dict[str, Any]:
        limit = max(1, min(int(limit or 100), 500))
        offset = max(0, int(offset or 0))
        async with pg_manager.get_async_session_context() as session:
            rows = (
                await session.execute(
                    select(KnowledgeRelationship)
                    .where(KnowledgeRelationship.db_id == db_id)
                    .order_by(KnowledgeRelationship.relation_type, KnowledgeRelationship.relationship_id)
                    .offset(offset)
                    .limit(limit + 1)
                )
            ).scalars().all()
        return {
            "items": [self.serialize_relationship(row) for row in rows[:limit]],
            "limit": limit,
            "offset": offset,
            "has_more": len(rows) > limit,
        }

    async def list_timeline(self, db_id: str, *, limit: int = 100, offset: int = 0) -> dict[str, Any]:
        limit = max(1, min(int(limit or 100), 500))
        offset = max(0, int(offset or 0))
        async with pg_manager.get_async_session_context() as session:
            rows = (
                await session.execute(
                    select(TemporalFact)
                    .where(TemporalFact.db_id == db_id)
                    .order_by(TemporalFact.occurred_at, TemporalFact.subject)
                    .offset(offset)
                    .limit(limit + 1)
                )
            ).scalars().all()
        return {
            "items": [self.serialize_temporal_fact(row) for row in rows[:limit]],
            "limit": limit,
            "offset": offset,
            "has_more": len(rows) > limit,
        }

    async def list_wiki_pages(self, db_id: str) -> list[WikiPage]:
        async with pg_manager.get_async_session_context() as session:
            rows = (
                await session.execute(select(WikiPage).where(WikiPage.db_id == db_id).order_by(WikiPage.page_type))
            ).scalars().all()
        return list(rows)

    async def replace_golden_set(self, db_id: str, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        async with pg_manager.get_async_session_context() as session:
            await session.execute(delete(GoldenSetItem).where(GoldenSetItem.db_id == db_id))
            for item in items:
                session.add(GoldenSetItem(**item))
        return items

    async def list_golden_set(self, db_id: str) -> list[GoldenSetItem]:
        async with pg_manager.get_async_session_context() as session:
            rows = (
                await session.execute(
                    select(GoldenSetItem)
                    .where(GoldenSetItem.db_id == db_id, GoldenSetItem.status == "active")
                    .order_by(GoldenSetItem.created_at)
                )
            ).scalars().all()
        return list(rows)

    async def insert_quality_gate_run(self, data: dict[str, Any]) -> QualityGateRun:
        run = QualityGateRun(**data)
        async with pg_manager.get_async_session_context() as session:
            session.add(run)
        return run

    async def get_quality_gate_run(self, db_id: str, gate_id: str) -> QualityGateRun | None:
        async with pg_manager.get_async_session_context() as session:
            result = await session.execute(
                select(QualityGateRun).where(QualityGateRun.db_id == db_id, QualityGateRun.gate_id == gate_id)
            )
            return result.scalar_one_or_none()

    async def insert_workflow_run(self, data: dict[str, Any]) -> WorldlineWorkflowRun:
        run = WorldlineWorkflowRun(**data)
        async with pg_manager.get_async_session_context() as session:
            session.add(run)
        return run

    async def insert_mcp_audit_log(self, data: dict[str, Any]) -> WorldlineMcpAuditLog:
        log = WorldlineMcpAuditLog(**data)
        async with pg_manager.get_async_session_context() as session:
            session.add(log)
        return log

    async def list_mcp_audit_logs(
        self,
        db_id: str,
        *,
        tool_name: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        limit = max(1, min(int(limit or 100), 500))
        offset = max(0, int(offset or 0))
        async with pg_manager.get_async_session_context() as session:
            stmt = (
                select(WorldlineMcpAuditLog)
                .where(WorldlineMcpAuditLog.db_id == db_id)
                .order_by(WorldlineMcpAuditLog.started_at.desc(), WorldlineMcpAuditLog.log_id)
                .offset(offset)
                .limit(limit + 1)
            )
            if tool_name:
                stmt = stmt.where(WorldlineMcpAuditLog.tool_name == tool_name)
            rows = (await session.execute(stmt)).scalars().all()
        return {
            "items": [self.serialize_mcp_audit_log(row) for row in rows[:limit]],
            "limit": limit,
            "offset": offset,
            "has_more": len(rows) > limit,
        }

    def serialize_entity(self, entity: KnowledgeEntity) -> dict[str, Any]:
        return {
            "entity_id": entity.entity_id,
            "db_id": entity.db_id,
            "name": entity.name,
            "entity_type": entity.entity_type,
            "aliases": entity.aliases or [],
            "evidence_ids": entity.evidence_ids or [],
            "source_chunk_ids": entity.source_chunk_ids or [],
            "status": entity.status,
            "metadata": entity.entity_metadata or {},
            "created_at": entity.created_at.isoformat() if entity.created_at else None,
            "updated_at": entity.updated_at.isoformat() if entity.updated_at else None,
        }

    def serialize_relationship(self, relationship: KnowledgeRelationship) -> dict[str, Any]:
        return {
            "relationship_id": relationship.relationship_id,
            "db_id": relationship.db_id,
            "source_entity_id": relationship.source_entity_id,
            "target_entity_id": relationship.target_entity_id,
            "relation_type": relationship.relation_type,
            "weight": relationship.weight,
            "evidence_ids": relationship.evidence_ids or [],
            "source_chunk_ids": relationship.source_chunk_ids or [],
            "status": relationship.status,
            "metadata": relationship.relationship_metadata or {},
            "created_at": relationship.created_at.isoformat() if relationship.created_at else None,
            "updated_at": relationship.updated_at.isoformat() if relationship.updated_at else None,
        }

    def serialize_temporal_fact(self, fact: TemporalFact) -> dict[str, Any]:
        return {
            "fact_id": fact.fact_id,
            "db_id": fact.db_id,
            "subject": fact.subject,
            "predicate": fact.predicate,
            "object": fact.object,
            "occurred_at": fact.occurred_at.isoformat() if fact.occurred_at else None,
            "source_entity_id": fact.source_entity_id,
            "evidence_ids": fact.evidence_ids or [],
            "source_chunk_ids": fact.source_chunk_ids or [],
            "confidence": fact.confidence,
            "metadata": fact.fact_metadata or {},
            "created_at": fact.created_at.isoformat() if fact.created_at else None,
        }

    def serialize_quality_gate_run(self, run: QualityGateRun) -> dict[str, Any]:
        return {
            "gate_id": run.gate_id,
            "db_id": run.db_id,
            "status": run.status,
            "thresholds": run.thresholds or {},
            "metrics": run.metrics or {},
            "coverage_map": run.coverage_map or {},
            "failure_replay": run.failure_replay or [],
            "tracing": run.tracing or {},
            "cost_stats": run.cost_stats or {},
            "latency_stats": run.latency_stats or {},
            "permission_checks": run.permission_checks or {},
            "created_by": run.created_by,
            "created_at": run.created_at.isoformat() if run.created_at else None,
            "completed_at": run.completed_at.isoformat() if run.completed_at else None,
        }

    def serialize_mcp_audit_log(self, log: WorldlineMcpAuditLog) -> dict[str, Any]:
        return {
            "log_id": log.log_id,
            "db_id": log.db_id,
            "tool_name": log.tool_name,
            "actor": log.actor,
            "status": log.status,
            "request_summary": log.request_summary or {},
            "result_summary": log.result_summary or {},
            "metadata": log.audit_metadata or {},
            "started_at": log.started_at.isoformat() if log.started_at else None,
            "completed_at": log.completed_at.isoformat() if log.completed_at else None,
        }
