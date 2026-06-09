from __future__ import annotations

from pathlib import Path

import pytest

from src.knowledge.compiler.models import CompiledDocument, CompiledEvidenceAnchor, CompiledNode
from src.knowledge.manager import KnowledgeBaseManager
from src.repositories.knowledge_graph_repository import KnowledgeGraphRepository
from src.repositories.knowledge_object_repository import KnowledgeObjectRepository
from src.services.auto_wiki_service import AutoWikiService
from src.services.knowledge_graph_service import KnowledgeGraphService
from src.services.worldline_agent_workflow_service import WorldlineAgentWorkflowService
from src.services.worldline_quality_gate_service import WorldlineQualityGateService
from src.services.worldline_workbench_service import WorldlineWorkbenchService
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


async def _seed_live_chunks(db_id: str = "kb_live", file_id: str = "file_live") -> None:
    text = (
        "# Live Worldline Notes\n\n"
        "AutoWiki Graph Timeline QualityGate shipped on 2026-06-03. "
        "Graph uses EvidenceAnchor citations and Timeline facts."
    )
    async with pg_manager.get_async_session_context() as session:
        session.add(KnowledgeBase(db_id=db_id, name="Live Worldline KB", kb_type="milvus"))
        session.add(KnowledgeFile(file_id=file_id, db_id=db_id, filename="live-worldline-notes.md"))

    compiled = CompiledDocument(
        source_uri="live-worldline-notes.md",
        title="live-worldline-notes.md",
        asset_type="file",
        markdown_content=text,
        parser="legacy_markdown",
        parser_version=None,
        status="success",
        content_hash="hash_live_content",
        ast_hash="hash_live_ast",
        parse_config={"db_id": db_id},
        parser_trace=[{"parser": "legacy_markdown", "status": "success"}],
        stats={"node_count": 2, "evidence_anchor_count": 2},
        nodes=[
            CompiledNode(key="n0", node_type="heading", node_order=0, text="# Live Worldline Notes"),
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
                source_uri="live-worldline-notes.md",
                text_excerpt="# Live Worldline Notes",
                confidence=1.0,
            ),
            CompiledEvidenceAnchor(
                node_key="n1",
                anchor_type="text",
                source_uri="live-worldline-notes.md",
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
                "filename": "live-worldline-notes.md",
                "source": "live-worldline-notes.md",
                "chunk_index": 0,
                "content": text,
            }
        ],
    )


async def _seed_conflicting_temporal_chunks(db_id: str = "kb_conflict", file_id: str = "file_conflict") -> None:
    first = "Graph shipped on 2026-06-03 with evidence path A."
    second = "Graph paused on 2026-06-03 because review path B was unresolved."
    text = "\n\n".join(["# Conflicting Graph Notes", first, second])

    async with pg_manager.get_async_session_context() as session:
        session.add(KnowledgeBase(db_id=db_id, name="Conflicting Graph KB", kb_type="milvus"))
        session.add(KnowledgeFile(file_id=file_id, db_id=db_id, filename="conflicting-graph-notes.md"))

    compiled = CompiledDocument(
        source_uri="conflicting-graph-notes.md",
        title="conflicting-graph-notes.md",
        asset_type="file",
        markdown_content=text,
        parser="legacy_markdown",
        parser_version=None,
        status="success",
        content_hash="hash_conflicting_content",
        ast_hash="hash_conflicting_ast",
        parse_config={"db_id": db_id},
        parser_trace=[{"parser": "legacy_markdown", "status": "success"}],
        stats={"node_count": 3, "evidence_anchor_count": 3},
        nodes=[
            CompiledNode(key="n0", node_type="heading", node_order=0, text="# Conflicting Graph Notes"),
            CompiledNode(key="n1", node_type="paragraph", node_order=1, text=first),
            CompiledNode(key="n2", node_type="paragraph", node_order=2, text=second),
        ],
        evidence_anchors=[
            CompiledEvidenceAnchor(
                node_key="n0",
                anchor_type="text",
                source_uri="conflicting-graph-notes.md",
                text_excerpt="# Conflicting Graph Notes",
                confidence=1.0,
            ),
            CompiledEvidenceAnchor(
                node_key="n1",
                anchor_type="text",
                source_uri="conflicting-graph-notes.md",
                text_excerpt=first,
                confidence=0.98,
            ),
            CompiledEvidenceAnchor(
                node_key="n2",
                anchor_type="text",
                source_uri="conflicting-graph-notes.md",
                text_excerpt=second,
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
                "filename": "conflicting-graph-notes.md",
                "source": "conflicting-graph-notes.md",
                "chunk_index": 0,
                "content": first,
            },
            {
                "id": f"{file_id}_chunk_1",
                "chunk_id": f"{file_id}_chunk_1",
                "file_id": file_id,
                "filename": "conflicting-graph-notes.md",
                "source": "conflicting-graph-notes.md",
                "chunk_index": 1,
                "content": second,
            },
        ],
    )


@pytest.mark.asyncio
async def test_live_graph_timeline_and_stale_detector(sqlite_pg_manager) -> None:
    await _seed_live_chunks()
    await AutoWikiService().rebuild_wiki("kb_live", max_topics=5)

    result = await KnowledgeGraphService().rebuild_graph("kb_live", max_entities=8)

    assert result["status"] == "success"
    assert result["counts"]["entities"] >= 3
    assert result["counts"]["relationships"] >= 1
    assert result["counts"]["temporal_facts"] == 1
    assert result["evidence_bound"]["entities"] == result["counts"]["entities"]

    timeline = await KnowledgeGraphService().list_timeline("kb_live")
    assert timeline["items"][0]["occurred_at"].startswith("2026-06-03")
    assert timeline["items"][0]["evidence_ids"]
    assert timeline["items"][0]["metadata"]["episode"]["episode_type"] == "temporal_fact"
    assert timeline["items"][0]["metadata"]["provenance"]["source"] == "EvidenceAnchor"
    assert timeline["items"][0]["metadata"]["validity_window"]["valid_from"].startswith("2026-06-03")

    entities = await KnowledgeGraphService().list_entities("kb_live")
    assert entities["items"][0]["metadata"]["episodes"][0]["episode_type"] == "entity_mention"
    assert entities["items"][0]["metadata"]["provenance"]["evidence_count"] >= 1
    assert entities["items"][0]["metadata"]["validity_window"]["basis"] == "source_doc_versions"

    relationships = await KnowledgeGraphService().list_relationships("kb_live")
    relationship = relationships["items"][0]
    assert relationship["source_entity_id"]
    assert relationship["target_entity_id"]
    assert relationship["evidence_ids"]
    assert relationship["metadata"]["episodes"][0]["episode_type"] == "relationship_co_mention"
    assert relationship["metadata"]["direction"] == "undirected_co_mention"

    conflicts = await KnowledgeGraphService().detect_temporal_conflicts("kb_live")
    assert conflicts["status"] == "clean"
    assert conflicts["conflict_count"] == 0

    projection = await KnowledgeGraphService().build_neo4j_projection("kb_live")
    assert projection["storage"]["target"] == "neo4j"
    assert projection["storage"]["write_enabled"] is False
    assert projection["nodes"]
    assert projection["relationships"]
    assert projection["temporal_facts"]
    assert projection["relationships"][0]["properties"]["evidence_ids"]
    assert projection["temporal_facts"][0]["properties"]["evidence_ids"]

    stale = await KnowledgeGraphService().detect_stale_pages("kb_live")
    assert stale["stale_count"] == 0
    assert stale["fresh_pages"] >= 4


@pytest.mark.asyncio
async def test_temporal_conflicts_are_reviewable_in_timeline_and_projection(sqlite_pg_manager) -> None:
    await _seed_conflicting_temporal_chunks()

    service = KnowledgeGraphService()
    result = await service.rebuild_graph("kb_conflict", max_entities=8)

    assert result["status"] == "success"
    assert result["counts"]["temporal_facts"] == 2
    assert result["conflicts"]["status"] == "needs_review"
    assert result["conflicts"]["conflict_count"] == 1

    conflicts = await service.detect_temporal_conflicts("kb_conflict")
    assert conflicts["status"] == "needs_review"
    assert conflicts["conflict_count"] == 1
    conflict = conflicts["items"][0]
    assert conflict["conflict_key"].endswith("|mentioned_on|2026-06-03")
    assert conflict["object_count"] == 2
    assert len(conflict["fact_ids"]) == 2
    assert conflict["evidence_ids"]
    assert len(conflict["objects"]) == 2

    timeline = await service.list_timeline("kb_conflict")
    reviewable = [item for item in timeline["items"] if item["conflict_status"] == "needs_review"]
    assert len(reviewable) == 2
    for item in reviewable:
        conflict_metadata = item["metadata"]["conflict"]
        assert conflict_metadata["status"] == "needs_review"
        assert set(conflict_metadata["related_fact_ids"]) == set(conflict["fact_ids"])
        assert conflict_metadata["object_count"] == 2
        assert conflict_metadata["evidence_ids"]

    projection = await service.build_neo4j_projection("kb_conflict")
    projected = [
        item
        for item in projection["temporal_facts"]
        if item["properties"].get("conflict", {}).get("status") == "needs_review"
    ]
    assert len(projected) == 2
    assert projection["storage"]["write_enabled"] is False


@pytest.mark.asyncio
async def test_worldline_manifest_and_workflow_plan(sqlite_pg_manager) -> None:
    await _seed_live_chunks()

    service = WorldlineAgentWorkflowService()
    manifest = service.tool_manifest()

    assert manifest["server"]["name"] == "worldline"
    assert manifest["runtime"]["orchestrator"] == "langgraph"
    assert manifest["runtime"]["async_dispatch"] == "arq"
    assert manifest["audit"]["enabled"] is True
    assert manifest["audit"]["table"] == "worldline_mcp_audit_logs"
    assert manifest["security"]["external_agents_direct_db_write"] is False
    assert manifest["subagents"]["single_writer_policy"] is True
    assert manifest["subagents"]["parallel_writes_to_same_files"] is False
    assert {lane["lane"] for lane in manifest["subagents"]["lanes"]} == {
        "research_reviewer",
        "knowledge_operator",
        "frontend_qa",
        "release_auditor",
    }
    artifact_tool = next(tool for tool in manifest["tools"] if tool["name"] == "worldline.inspect_run_artifacts")
    assert artifact_tool["write_scope"] == "none"
    assert artifact_tool["dispatch_backend"] == "inline"
    assert "audit_db_id" in artifact_tool["input_schema"]["properties"]
    gate_tool = next(tool for tool in manifest["tools"] if tool["name"] == "worldline.inspect_run_gates")
    assert gate_tool["write_scope"] == "none"
    assert gate_tool["dispatch_backend"] == "inline"
    assert "gate_id" in gate_tool["input_schema"]["properties"]
    assert "audit_db_id" in gate_tool["input_schema"]["properties"]
    evidence_tool = next(tool for tool in manifest["tools"] if tool["name"] == "worldline.inspect_run_evidence")
    assert evidence_tool["write_scope"] == "none"
    assert evidence_tool["dispatch_backend"] == "inline"
    assert "evidence_id" in evidence_tool["input_schema"]["properties"]
    assert "source_id" in evidence_tool["input_schema"]["properties"]
    assert "audit_db_id" in evidence_tool["input_schema"]["properties"]
    knowledge_tool = next(tool for tool in manifest["tools"] if tool["name"] == "worldline.inspect_run_knowledge")
    assert knowledge_tool["write_scope"] == "none"
    assert knowledge_tool["dispatch_backend"] == "inline"
    assert "kind" in knowledge_tool["input_schema"]["properties"]
    assert "item_id" in knowledge_tool["input_schema"]["properties"]
    assert "audit_db_id" in knowledge_tool["input_schema"]["properties"]
    run_manifest_tool = next(tool for tool in manifest["tools"] if tool["name"] == "worldline.inspect_run_manifest")
    assert run_manifest_tool["write_scope"] == "none"
    assert run_manifest_tool["dispatch_backend"] == "inline"
    assert "include_resources" in run_manifest_tool["input_schema"]["properties"]
    assert "audit_db_id" in run_manifest_tool["input_schema"]["properties"]
    assert all(tool["requires_admin"] for tool in manifest["tools"] if tool["write_scope"] != "none")

    plan = await service.plan_workflow(
        "kb_live",
        requested_steps=["worldline.rebuild_wiki", "worldline.update_graph"],
    )

    assert plan["orchestrator"] == "langgraph"
    assert plan["dispatch_backend"] == "arq"
    assert [node["tool"] for node in plan["nodes"]] == ["worldline.rebuild_wiki", "worldline.update_graph"]
    assert plan["edges"] == [{"from": "n0_rebuild_wiki", "to": "n1_update_graph", "condition": "success"}]

    audit_logs = await service.list_audit_logs("kb_live", tool_name="worldline.plan_workflow")
    assert len(audit_logs["items"]) == 1
    assert audit_logs["items"][0]["status"] == "success"
    assert audit_logs["items"][0]["result_summary"]["tool_count"] == 2


@pytest.mark.asyncio
async def test_database_info_falls_back_when_backend_metadata_is_missing(
    sqlite_pg_manager,
    monkeypatch,
    tmp_path: Path,
) -> None:
    async with pg_manager.get_async_session_context() as session:
        session.add(
            KnowledgeBase(
                db_id="kb_info_fallback",
                name="Info Fallback KB",
                description="Repository metadata exists even if backend metadata is missing.",
                kb_type="milvus",
                additional_params={"chunk_size": 640},
                query_params={"top_k": 5},
            )
        )

    class MissingBackendMetadata:
        def get_database_info(self, db_id: str):
            return None

    async def fake_get_kb_for_database(self, db_id: str):
        return MissingBackendMetadata()

    monkeypatch.setattr(KnowledgeBaseManager, "_get_kb_for_database", fake_get_kb_for_database)

    info = await KnowledgeBaseManager(str(tmp_path / "kb-manager")).get_database_info("kb_info_fallback")

    assert info["db_id"] == "kb_info_fallback"
    assert info["name"] == "Info Fallback KB"
    assert info["kb_type"] == "milvus"
    assert info["status"] == "metadata_unavailable"
    assert info["additional_params"]["chunk_size"] == 640
    assert info["query_params"] == {"top_k": 5}


@pytest.mark.asyncio
async def test_quality_gate_builds_golden_set_and_replay(sqlite_pg_manager) -> None:
    await _seed_live_chunks()
    await AutoWikiService().rebuild_wiki("kb_live", max_topics=5)
    await KnowledgeGraphService().rebuild_graph("kb_live", max_entities=8)

    gate_service = WorldlineQualityGateService()
    golden = await gate_service.build_golden_set("kb_live")
    gate = await gate_service.run_gate("kb_live")

    assert golden["item_count"] >= 1
    assert gate["status"] == "passed"
    assert gate["metrics"]["evidence_accuracy"] >= 0.95
    assert gate["metrics"]["faithfulness"] >= 0.90
    assert gate["metrics"]["context_recall"] >= 0.85
    assert gate["metrics"]["context_precision"] >= 0.80
    assert gate["metrics"]["golden_item_count"] >= 1
    assert gate["metrics"]["stale_page_count"] == 0
    assert gate["metrics"]["temporal_conflict_count"] == 0
    assert gate["coverage_map"]["graph"]["covered"] is True
    assert gate["coverage_map"]["graph"]["conflicts"] == 0
    assert gate["coverage_map"]["timeline"]["covered"] is True
    assert gate["coverage_map"]["wiki"]["covered"] is True
    assert gate["coverage_map"]["production"]["permission_checks"] is True
    assert gate["failure_replay"] == []
    assert gate["cost_stats"]["estimated_usd"] == 0.0
    assert gate["latency_stats"]["total_ms"] >= 0

    stored = await KnowledgeGraphRepository().get_quality_gate_run("kb_live", gate["gate_id"])
    assert stored is not None


@pytest.mark.asyncio
async def test_quality_gate_intentional_failure_has_replay_refs(sqlite_pg_manager) -> None:
    await _seed_live_chunks()
    await AutoWikiService().rebuild_wiki("kb_live", max_topics=5)
    await KnowledgeGraphService().rebuild_graph("kb_live", max_entities=8)

    gate_service = WorldlineQualityGateService()
    await gate_service.build_golden_set("kb_live")
    gate = await gate_service.run_gate(
        "kb_live",
        thresholds={
            "evidence_accuracy_min": 1.01,
            "faithfulness_min": 1.01,
            "context_recall_min": 1.01,
            "context_precision_min": 1.01,
        },
        created_by="pytest-intentional-failure",
    )

    assert gate["status"] == "failed"
    assert {item["check"] for item in gate["failure_replay"]} >= {
        "evidence_accuracy",
        "faithfulness",
        "context_recall",
        "context_precision",
    }

    replay = gate["failure_replay"][0]
    assert replay["reason"]
    assert replay["severity"] in {"high", "medium", "warning"}
    assert replay["replay"]["body"]["thresholds"]["evidence_accuracy_min"] == 1.01

    refs = replay["refs"]
    for ref_kind in ("evidence", "wiki", "graph", "timeline", "run"):
        assert refs[ref_kind]

    target_kinds = {target["kind"] for target in replay["jump_targets"]}
    assert target_kinds >= {"evidence", "wiki", "graph", "timeline", "run"}
    assert refs["run"][0]["gate_id"] == gate["gate_id"]
    assert refs["evidence"][0]["evidence_id"]
    assert refs["wiki"][0]["page_id"]
    assert refs["graph"][0]["entity_id"]
    assert refs["timeline"][0]["fact_id"]

    stored = await KnowledgeGraphRepository().get_quality_gate_run("kb_live", gate["gate_id"])
    assert stored is not None
    serialized = KnowledgeGraphRepository().serialize_quality_gate_run(stored)
    assert serialized["failure_replay"][0]["refs"]["run"][0]["gate_id"] == gate["gate_id"]


@pytest.mark.asyncio
async def test_workbench_overview_and_generate(sqlite_pg_manager) -> None:
    await _seed_live_chunks()
    await AutoWikiService().rebuild_wiki("kb_live", max_topics=5)
    await KnowledgeGraphService().rebuild_graph("kb_live", max_entities=8)
    await WorldlineQualityGateService().run_gate("kb_live")

    service = WorldlineWorkbenchService()
    overview = await service.build_overview("kb_live")

    assert overview["status"] == "ready"
    assert overview["counts"]["evidence_anchors"] >= 2
    assert overview["counts"]["wiki_pages"] >= 1
    assert overview["counts"]["entities"] >= 1
    assert overview["mcp"]["manifest"]["server"]["name"] == "worldline"
    assert overview["quality_gate"]["latest"]["status"] == "passed"

    result = await service.generate_worldline(
        "kb_live",
        theme_id="knowledge-ops",
        question="How should recovery validation proceed?",
    )

    assert result["status"] == "ready"
    assert result["themeId"] == "knowledge-ops"
    assert result["knowledgeDbId"] == "kb_live"
    assert result["branches"]
    assert result["tree"]["nodes"]
    assert result["branches"][0]["evidenceRefs"]
    assert result["knowledgeMode"] == "llm_wiki_primary_rag_auxiliary"
    assert "llm_wiki" in result["layers"]
    assert result["branches"][0]["wikiRefs"]
    assert result["branches"][0]["entityRefs"]
    assert result["branches"][0]["timelineRefs"]
    graph_branch = next(branch for branch in result["branches"] if branch["entityRefs"] or branch["timelineRefs"])
    graph_action = next(action for action in graph_branch["nextActions"] if action["targetType"] == "graph")
    assert graph_action["id"].endswith("-graph")
    assert graph_branch["context"]["db_id"] == "kb_live"
    assert graph_branch["context"]["knowledge_db_id"] == "kb_live"
    assert graph_branch["entityRefs"][0]["id"]
    assert graph_branch["entityRefs"][0]["evidenceId"]
    assert graph_branch["timelineRefs"][0]["id"]
    assert graph_branch["timelineRefs"][0]["evidenceId"]
    assert result["branches"][0]["quality"]["citationCoverage"] > 0
    assert result["snapshots"]
    assert result["quality"]["branchCount"] == len(result["branches"])
    assert result["routeTrace"]["deterministic_baseline"] is True
