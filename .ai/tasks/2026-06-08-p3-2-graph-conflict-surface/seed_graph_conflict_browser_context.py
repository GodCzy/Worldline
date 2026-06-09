from __future__ import annotations

import asyncio
import json
import os
from datetime import UTC, datetime

from sqlalchemy import select

from src.knowledge.compiler.models import CompiledDocument, CompiledEvidenceAnchor, CompiledNode
from src.repositories.knowledge_object_repository import KnowledgeObjectRepository
from src.services.knowledge_graph_service import KnowledgeGraphService
from src.storage.postgres.manager import pg_manager
from src.storage.postgres.models_knowledge import KnowledgeBase, KnowledgeFile


def _default_db_id() -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    return f"kb_codex_graph_conflict_{stamp}"


DB_ID = os.getenv("WORLDLINE_GRAPH_CONFLICT_DB_ID", "").strip() or _default_db_id()
FILE_ID = f"file_{DB_ID[-32:]}"
FILENAME = "codex-graph-conflict-notes.md"


async def seed() -> dict[str, object]:
    first = "Graph shipped on 2026-06-03 with evidence path A."
    second = "Graph paused on 2026-06-03 because review path B was unresolved."
    text = "\n\n".join(["# Codex Graph Conflict Notes", first, second])

    pg_manager.initialize()
    await pg_manager.ensure_knowledge_schema()

    async with pg_manager.get_async_session_context() as session:
        existing = (await session.execute(select(KnowledgeBase).where(KnowledgeBase.db_id == DB_ID))).scalar_one_or_none()
        if existing is not None:
            await session.delete(existing)
            await session.flush()

        session.add(
            KnowledgeBase(
                db_id=DB_ID,
                name="Codex Graph Conflict QA KB",
                description="Temporary Worldline graph conflict browser QA knowledge base.",
                kb_type="lightrag",
                additional_params={"codex_temp": True, "purpose": "graph_conflict_surface_browser_qa"},
                share_config={"is_shared": True, "accessible_departments": []},
            )
        )
        session.add(
            KnowledgeFile(
                file_id=FILE_ID,
                db_id=DB_ID,
                filename=FILENAME,
                original_filename=FILENAME,
                file_type="md",
                status="processed",
                content_hash=f"hash_{DB_ID}",
                file_size=len(text.encode("utf-8")),
                content_type="text/markdown",
            )
        )

    compiled = CompiledDocument(
        source_uri=FILENAME,
        title=FILENAME,
        asset_type="file",
        markdown_content=text,
        parser="legacy_markdown",
        parser_version=None,
        status="success",
        content_hash=f"hash_content_{DB_ID}",
        ast_hash=f"hash_ast_{DB_ID}",
        parse_config={"db_id": DB_ID},
        parser_trace=[{"parser": "legacy_markdown", "status": "success"}],
        stats={"node_count": 3, "evidence_anchor_count": 3},
        nodes=[
            CompiledNode(key="n0", node_type="heading", node_order=0, text="# Codex Graph Conflict Notes"),
            CompiledNode(key="n1", node_type="paragraph", node_order=1, text=first),
            CompiledNode(key="n2", node_type="paragraph", node_order=2, text=second),
        ],
        evidence_anchors=[
            CompiledEvidenceAnchor(
                node_key="n0",
                anchor_type="text",
                source_uri=FILENAME,
                text_excerpt="# Codex Graph Conflict Notes",
                confidence=1.0,
            ),
            CompiledEvidenceAnchor(
                node_key="n1",
                anchor_type="text",
                source_uri=FILENAME,
                text_excerpt=first,
                confidence=0.98,
            ),
            CompiledEvidenceAnchor(
                node_key="n2",
                anchor_type="text",
                source_uri=FILENAME,
                text_excerpt=second,
                confidence=0.98,
            ),
        ],
    )

    object_repository = KnowledgeObjectRepository()
    await object_repository.persist_compiled_document(DB_ID, FILE_ID, compiled)
    await object_repository.bind_chunks_to_latest_evidence(
        DB_ID,
        FILE_ID,
        [
            {
                "id": f"{FILE_ID}_chunk_0",
                "chunk_id": f"{FILE_ID}_chunk_0",
                "file_id": FILE_ID,
                "filename": FILENAME,
                "source": FILENAME,
                "chunk_index": 0,
                "content": first,
            },
            {
                "id": f"{FILE_ID}_chunk_1",
                "chunk_id": f"{FILE_ID}_chunk_1",
                "file_id": FILE_ID,
                "filename": FILENAME,
                "source": FILENAME,
                "chunk_index": 1,
                "content": second,
            },
        ],
    )

    service = KnowledgeGraphService()
    rebuild = await service.rebuild_graph(DB_ID, max_entities=8)
    entities = await service.list_entities(DB_ID)
    relationships = await service.list_relationships(DB_ID)
    timeline = await service.list_timeline(DB_ID)
    conflicts = await service.detect_temporal_conflicts(DB_ID)

    return {
        "status": "ok",
        "db_id": DB_ID,
        "file_id": FILE_ID,
        "browser_url": f"http://127.0.0.1:5173/graph?db_id={DB_ID}&knowledge_db_id={DB_ID}",
        "rebuild_counts": rebuild.get("counts"),
        "entities": len(entities.get("items") or []),
        "relationships": len(relationships.get("items") or []),
        "timeline": len(timeline.get("items") or []),
        "conflict_status": conflicts.get("status"),
        "conflict_count": conflicts.get("conflict_count"),
        "fact_ids": [
            fact.get("fact_id")
            for fact in timeline.get("items") or []
            if fact.get("conflict_status") == "needs_review"
        ],
        "evidence_ids": sorted({item for conflict in conflicts.get("items") or [] for item in conflict.get("evidence_ids") or []}),
    }


async def main() -> int:
    try:
        print(json.dumps(await seed(), ensure_ascii=False, indent=2))
        return 0
    finally:
        await pg_manager.close()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
