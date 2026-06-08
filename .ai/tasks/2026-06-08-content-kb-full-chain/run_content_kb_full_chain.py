from __future__ import annotations

import asyncio
import hashlib
import json
import os
import time
from typing import Any

from sqlalchemy import func, select

from src.knowledge.compiler.models import CompiledDocument, CompiledEvidenceAnchor, CompiledNode
from src.repositories.knowledge_object_repository import KnowledgeObjectRepository
from src.services.auto_wiki_service import AutoWikiService
from src.services.knowledge_graph_service import KnowledgeGraphService
from src.services.worldline_quality_gate_service import WorldlineQualityGateService
from src.services.worldline_workbench_service import WorldlineWorkbenchService
from src.storage.postgres.manager import pg_manager
from src.storage.postgres.models_knowledge import (
    DocumentNode,
    DocumentVersion,
    EvidenceAnchor,
    GoldenSetItem,
    KnowledgeBase,
    KnowledgeChunk,
    KnowledgeEntity,
    KnowledgeFile,
    KnowledgeRelationship,
    QualityGateRun,
    SourceAsset,
    TemporalFact,
    WikiPage,
)


RUN_STAMP = os.getenv("WORLDLINE_CONTENT_KB_STAMP") or str(int(time.time()))
DB_ID = os.getenv("WORLDLINE_CONTENT_KB_DB_ID") or f"codex_content_kb_{RUN_STAMP}"
FILE_ID = os.getenv("WORLDLINE_CONTENT_KB_FILE_ID") or f"codex_file_{RUN_STAMP}"
THEME_ID = os.getenv("WORLDLINE_CONTENT_KB_THEME_ID") or f"codex-content-{RUN_STAMP}"


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _source_text() -> str:
    return "\n".join(
        [
            "# Codex Content Knowledge Chain",
            "",
            "On 2026-06-03, AutoWiki connected EvidenceAnchor citations to Worldline recovery branches.",
            "On 2026-06-04, GraphService linked TemporalFact timelines with QualityGate replay evidence.",
            "On 2026-06-08, Codex validates the SourceAsset, DocumentVersion, DocumentNode, EvidenceAnchor, KnowledgeChunk, WikiPage, KnowledgeEntity, KnowledgeRelationship, TemporalFact, QualityGateRun, and Worldline chain.",
            "The recovery decision compares AutoWiki, GraphService, Timeline, QualityGate, and AgentLedger signals before a live UI screenshot is accepted.",
        ]
    )


async def _cleanup_existing(db_id: str) -> None:
    async with pg_manager.get_async_session_context() as session:
        result = await session.execute(select(KnowledgeBase).where(KnowledgeBase.db_id == db_id))
        kb = result.scalar_one_or_none()
        if kb is not None:
            await session.delete(kb)


async def _seed_document() -> dict[str, Any]:
    text = _source_text()
    paragraphs = [line for line in text.splitlines() if line.strip()]
    nodes = [
        CompiledNode(key=f"n{index}", node_type="heading" if line.startswith("#") else "paragraph", node_order=index, text=line)
        for index, line in enumerate(paragraphs)
    ]
    anchors = [
        CompiledEvidenceAnchor(
            node_key=node.key,
            anchor_type="text",
            source_uri="codex-content-chain.md",
            text_excerpt=node.text,
            confidence=1.0 if node.node_type == "heading" else 0.98,
            line_start=index + 1,
            line_end=index + 1,
        )
        for index, node in enumerate(nodes)
    ]

    async with pg_manager.get_async_session_context() as session:
        session.add(
            KnowledgeBase(
                db_id=DB_ID,
                name="Codex Content KB Full Chain",
                description="Temporary QA knowledge base for evidence-bound Worldline validation.",
                kb_type="milvus",
                additional_params={"chunk_size": 800, "chunk_overlap": 120, "qa_separator": "\n---\n"},
                query_params={"top_k": 5, "score_threshold": 0.2},
                share_config={"scope": "private", "qa": "codex-content-kb-full-chain"},
            )
        )
        session.add(
            KnowledgeFile(
                file_id=FILE_ID,
                db_id=DB_ID,
                filename="codex-content-chain.md",
                original_filename="codex-content-chain.md",
                file_type="md",
                status="parsed",
                content_hash=_hash(text),
                processing_params={"chunk_size": 800, "chunk_overlap": 120, "parser": "legacy_markdown"},
            )
        )

    compiled = CompiledDocument(
        source_uri="codex-content-chain.md",
        title="codex-content-chain.md",
        asset_type="file",
        markdown_content=text,
        parser="legacy_markdown",
        parser_version="codex-live-qa-v1",
        status="success",
        content_hash=_hash(text),
        ast_hash=_hash(json.dumps([node.text for node in nodes], ensure_ascii=False)),
        parse_config={"db_id": DB_ID, "chunk_size": 800, "chunk_overlap": 120},
        parser_trace=[{"parser": "legacy_markdown", "status": "success", "source": "codex-live-qa"}],
        stats={"node_count": len(nodes), "evidence_anchor_count": len(anchors), "char_count": len(text)},
        nodes=nodes,
        evidence_anchors=anchors,
    )
    persisted = await KnowledgeObjectRepository().persist_compiled_document(DB_ID, FILE_ID, compiled, owner="codex")
    chunks = await KnowledgeObjectRepository().bind_chunks_to_latest_evidence(
        DB_ID,
        FILE_ID,
        [
            {
                "id": f"{FILE_ID}_chunk_0",
                "chunk_id": f"{FILE_ID}_chunk_0",
                "file_id": FILE_ID,
                "filename": "codex-content-chain.md",
                "source": "codex-content-chain.md",
                "chunk_index": 0,
                "content": text,
                "metadata": {"qa_task": "content-kb-full-chain"},
            }
        ],
    )
    return {"persisted": persisted, "chunk_count": len(chunks), "text_chars": len(text)}


async def _counts() -> dict[str, int]:
    async with pg_manager.get_async_session_context() as session:
        source_assets = await session.scalar(select(func.count()).select_from(SourceAsset).where(SourceAsset.db_id == DB_ID))
        document_versions = await session.scalar(
            select(func.count())
            .select_from(DocumentVersion)
            .join(SourceAsset, DocumentVersion.asset_id == SourceAsset.asset_id)
            .where(SourceAsset.db_id == DB_ID)
        )
        document_nodes = await session.scalar(
            select(func.count())
            .select_from(DocumentNode)
            .join(DocumentVersion, DocumentNode.doc_version_id == DocumentVersion.doc_version_id)
            .join(SourceAsset, DocumentVersion.asset_id == SourceAsset.asset_id)
            .where(SourceAsset.db_id == DB_ID)
        )
        evidence_anchors = await session.scalar(
            select(func.count())
            .select_from(EvidenceAnchor)
            .join(DocumentVersion, EvidenceAnchor.doc_version_id == DocumentVersion.doc_version_id)
            .join(SourceAsset, DocumentVersion.asset_id == SourceAsset.asset_id)
            .where(SourceAsset.db_id == DB_ID)
        )
        knowledge_chunks = await session.scalar(select(func.count()).select_from(KnowledgeChunk).where(KnowledgeChunk.db_id == DB_ID))
        wiki_pages = await session.scalar(select(func.count()).select_from(WikiPage).where(WikiPage.db_id == DB_ID))
        entities = await session.scalar(select(func.count()).select_from(KnowledgeEntity).where(KnowledgeEntity.db_id == DB_ID))
        relationships = await session.scalar(select(func.count()).select_from(KnowledgeRelationship).where(KnowledgeRelationship.db_id == DB_ID))
        temporal_facts = await session.scalar(select(func.count()).select_from(TemporalFact).where(TemporalFact.db_id == DB_ID))
        golden_items = await session.scalar(select(func.count()).select_from(GoldenSetItem).where(GoldenSetItem.db_id == DB_ID))
        quality_gate_runs = await session.scalar(select(func.count()).select_from(QualityGateRun).where(QualityGateRun.db_id == DB_ID))

    return {
        "source_assets": int(source_assets or 0),
        "document_versions": int(document_versions or 0),
        "document_nodes": int(document_nodes or 0),
        "evidence_anchors": int(evidence_anchors or 0),
        "knowledge_chunks": int(knowledge_chunks or 0),
        "wiki_pages": int(wiki_pages or 0),
        "entities": int(entities or 0),
        "relationships": int(relationships or 0),
        "temporal_facts": int(temporal_facts or 0),
        "golden_items": int(golden_items or 0),
        "quality_gate_runs": int(quality_gate_runs or 0),
    }


async def run() -> dict[str, Any]:
    pg_manager.initialize()
    await pg_manager.ensure_knowledge_schema()
    await _cleanup_existing(DB_ID)
    seed = await _seed_document()

    wiki = await AutoWikiService().rebuild_wiki(DB_ID, max_topics=8)
    graph = await KnowledgeGraphService().rebuild_graph(DB_ID, max_entities=20)
    gate_service = WorldlineQualityGateService()
    golden = await gate_service.build_golden_set(DB_ID)
    gate = await gate_service.run_gate(DB_ID, created_by="codex-live-qa")
    overview = await WorldlineWorkbenchService().build_overview(DB_ID)
    worldline = await WorldlineWorkbenchService().generate_worldline(
        DB_ID,
        theme_id=THEME_ID,
        question="How should the evidence-backed Worldline recovery chain be validated?",
        context={
            "objective": "Validate non-empty KB chain from evidence ledger to Worldline UI.",
            "evidence_sources": ["codex-content-chain.md"],
        },
    )
    counts = await _counts()

    for key in (
        "source_assets",
        "document_versions",
        "document_nodes",
        "evidence_anchors",
        "knowledge_chunks",
        "wiki_pages",
        "entities",
        "relationships",
        "temporal_facts",
        "golden_items",
        "quality_gate_runs",
    ):
        _expect(counts[key] > 0, f"Expected non-zero {key}, got {counts[key]}")

    _expect(wiki["status"] == "success", f"Wiki rebuild failed: {wiki}")
    _expect(graph["status"] == "success", f"Graph rebuild failed: {graph}")
    _expect(golden["item_count"] > 0, "Golden set is empty")
    _expect(gate["status"] == "passed", f"Quality gate did not pass: {gate}")
    _expect(overview["status"] == "ready", f"Overview not ready: {overview.get('status')}")
    _expect(worldline["status"] == "ready", f"Worldline not ready: {worldline.get('status')}")
    _expect(bool(worldline.get("branches")), "Worldline branches are empty")
    first_branch = worldline["branches"][0]
    _expect(bool(first_branch.get("evidenceRefs")), "Branch missing evidenceRefs")
    _expect(bool(first_branch.get("wikiRefs")), "Branch missing wikiRefs")
    _expect(bool(first_branch.get("entityRefs")), "Branch missing entityRefs")
    _expect(bool(first_branch.get("timelineRefs")), "Branch missing timelineRefs")

    return {
        "status": "ok",
        "db_id": DB_ID,
        "file_id": FILE_ID,
        "theme_id": THEME_ID,
        "seed": seed,
        "counts": counts,
        "wiki": {"status": wiki["status"], "page_counts": wiki["page_counts"], "pages": len(wiki["pages"])},
        "graph": {"status": graph["status"], "counts": graph["counts"], "evidence_bound": graph.get("evidence_bound")},
        "golden": {"status": golden["status"], "item_count": golden["item_count"]},
        "gate": {
            "status": gate["status"],
            "gate_id": gate["gate_id"],
            "metrics": gate["metrics"],
            "failure_replay": gate["failure_replay"],
        },
        "overview": {"status": overview["status"], "counts": overview["counts"]},
        "worldline": {
            "status": worldline["status"],
            "themeId": worldline["themeId"],
            "knowledgeDbId": worldline["knowledgeDbId"],
            "branch_count": len(worldline["branches"]),
            "first_branch": {
                "id": first_branch.get("id"),
                "evidenceRefs": len(first_branch.get("evidenceRefs") or []),
                "wikiRefs": len(first_branch.get("wikiRefs") or []),
                "entityRefs": len(first_branch.get("entityRefs") or []),
                "timelineRefs": len(first_branch.get("timelineRefs") or []),
            },
            "routeTrace": worldline.get("routeTrace"),
        },
        "browser_url": f"http://127.0.0.1:5173/worldline/{THEME_ID}?theme={THEME_ID}&module={THEME_ID}&db_id={DB_ID}&knowledge_db_id={DB_ID}",
    }


async def main() -> int:
    try:
        result = await run()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    finally:
        await pg_manager.close()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
