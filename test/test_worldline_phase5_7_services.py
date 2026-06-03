from __future__ import annotations

from pathlib import Path

import pytest

from src.knowledge.compiler.models import CompiledDocument, CompiledEvidenceAnchor, CompiledNode
from src.repositories.knowledge_graph_repository import KnowledgeGraphRepository
from src.repositories.knowledge_object_repository import KnowledgeObjectRepository
from src.services.auto_wiki_service import AutoWikiService
from src.services.knowledge_graph_service import KnowledgeGraphService
from src.services.worldline_agent_workflow_service import WorldlineAgentWorkflowService
from src.services.worldline_quality_gate_service import WorldlineQualityGateService
from src.storage.postgres.manager import pg_manager
from src.storage.postgres.models_knowledge import KnowledgeBase, KnowledgeFile


@pytest.fixture()
async def sqlite_pg_manager(monkeypatch, tmp_path: Path):
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


async def _seed_phase5_chunks(db_id: str = "kb_phase5", file_id: str = "file_phase5") -> None:
    text = (
        "# Phase 5 Notes\n\n"
        "AutoWiki Graph Timeline QualityGate shipped on 2026-06-03. "
        "Graph uses EvidenceAnchor citations and Timeline facts."
    )
    async with pg_manager.get_async_session_context() as session:
        session.add(KnowledgeBase(db_id=db_id, name="Phase 5 KB", kb_type="milvus"))
        session.add(KnowledgeFile(file_id=file_id, db_id=db_id, filename="phase5-notes.md"))

    compiled = CompiledDocument(
        source_uri="phase5-notes.md",
        title="phase5-notes.md",
        asset_type="file",
        markdown_content=text,
        parser="legacy_markdown",
        parser_version=None,
        status="success",
        content_hash="hash_phase5_content",
        ast_hash="hash_phase5_ast",
        parse_config={"db_id": db_id},
        parser_trace=[{"parser": "legacy_markdown", "status": "success"}],
        stats={"node_count": 2, "evidence_anchor_count": 2},
        nodes=[
            CompiledNode(key="n0", node_type="heading", node_order=0, text="# Phase 5 Notes"),
            CompiledNode(
                key="n1",
                node_type="paragraph",
                node_order=1,
                text=(
                    "AutoWiki Graph Timeline QualityGate shipped on 2026-06-03. "
                    "Graph uses EvidenceAnchor citations and Timeline facts."
                ),
            ),
        ],
        evidence_anchors=[
            CompiledEvidenceAnchor(
                node_key="n0",
                anchor_type="text",
                source_uri="phase5-notes.md",
                text_excerpt="# Phase 5 Notes",
                confidence=1.0,
            ),
            CompiledEvidenceAnchor(
                node_key="n1",
                anchor_type="text",
                source_uri="phase5-notes.md",
                text_excerpt=(
                    "AutoWiki Graph Timeline QualityGate shipped on 2026-06-03. "
                    "Graph uses EvidenceAnchor citations and Timeline facts."
                ),
                confidence=0.98,
            ),
        ],
    )
    await KnowledgeObjectRepository().persist_compiled_document(db_id, file_id, compiled)
    await KnowledgeObjectRepository().bind_chunks_to_latest_evidence(
        db_id,
        file_id,
        [
            {
                "id": f"{file_id}_chunk_0",
                "chunk_id": f"{file_id}_chunk_0",
                "file_id": file_id,
                "filename": "phase5-notes.md",
                "source": "phase5-notes.md",
                "chunk_index": 0,
                "content": text,
            }
        ],
    )


@pytest.mark.asyncio
async def test_phase5_graph_timeline_and_stale_detector(sqlite_pg_manager) -> None:
    await _seed_phase5_chunks()
    await AutoWikiService().rebuild_wiki("kb_phase5", max_topics=5)

    result = await KnowledgeGraphService().rebuild_graph("kb_phase5", max_entities=8)

    assert result["status"] == "success"
    assert result["counts"]["entities"] >= 3
    assert result["counts"]["relationships"] >= 1
    assert result["counts"]["temporal_facts"] == 1
    assert result["evidence_bound"]["entities"] == result["counts"]["entities"]

    timeline = await KnowledgeGraphService().list_timeline("kb_phase5")
    assert timeline["items"][0]["occurred_at"].startswith("2026-06-03")
    assert timeline["items"][0]["evidence_ids"]

    stale = await KnowledgeGraphService().detect_stale_pages("kb_phase5")
    assert stale["stale_count"] == 0
    assert stale["fresh_pages"] >= 4


@pytest.mark.asyncio
async def test_phase6_worldline_manifest_and_workflow_plan(sqlite_pg_manager) -> None:
    await _seed_phase5_chunks()

    service = WorldlineAgentWorkflowService()
    manifest = service.tool_manifest()

    assert manifest["server"]["name"] == "worldline"
    assert manifest["runtime"]["orchestrator"] == "langgraph"
    assert manifest["runtime"]["async_dispatch"] == "arq"
    assert manifest["security"]["external_agents_direct_db_write"] is False
    assert all(tool["requires_admin"] for tool in manifest["tools"] if tool["write_scope"] != "none")

    plan = await service.plan_workflow(
        "kb_phase5",
        requested_steps=["worldline.rebuild_wiki", "worldline.update_graph"],
    )

    assert plan["orchestrator"] == "langgraph"
    assert plan["dispatch_backend"] == "arq"
    assert [node["tool"] for node in plan["nodes"]] == ["worldline.rebuild_wiki", "worldline.update_graph"]
    assert plan["edges"] == [{"from": "n0_rebuild_wiki", "to": "n1_update_graph", "condition": "success"}]


@pytest.mark.asyncio
async def test_phase7_quality_gate_builds_golden_set_and_replay(sqlite_pg_manager) -> None:
    await _seed_phase5_chunks()
    await AutoWikiService().rebuild_wiki("kb_phase5", max_topics=5)
    await KnowledgeGraphService().rebuild_graph("kb_phase5", max_entities=8)

    gate_service = WorldlineQualityGateService()
    golden = await gate_service.build_golden_set("kb_phase5")
    gate = await gate_service.run_gate("kb_phase5")

    assert golden["item_count"] >= 1
    assert gate["status"] == "passed"
    assert gate["metrics"]["evidence_accuracy"] >= 0.95
    assert gate["metrics"]["golden_item_count"] >= 1
    assert gate["metrics"]["stale_page_count"] == 0
    assert gate["coverage_map"]["graph"]["covered"] is True
    assert gate["coverage_map"]["timeline"]["covered"] is True
    assert gate["coverage_map"]["wiki"]["covered"] is True
    assert gate["coverage_map"]["production"]["permission_checks"] is True
    assert gate["failure_replay"] == []
    assert gate["cost_stats"]["estimated_usd"] == 0.0
    assert gate["latency_stats"]["total_ms"] >= 0

    stored = await KnowledgeGraphRepository().get_quality_gate_run("kb_phase5", gate["gate_id"])
    assert stored is not None
