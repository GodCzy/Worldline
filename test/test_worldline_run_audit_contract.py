from __future__ import annotations

from pathlib import Path

import pytest

from src.services.worldline_agent_workflow_service import WorldlineAgentWorkflowService
from src.services.worldline_run_ledger_service import WorldlineRunLedgerService
from src.storage.postgres.manager import pg_manager
from src.storage.postgres.models_knowledge import KnowledgeBase


@pytest.fixture()
async def sqlite_pg_manager(monkeypatch, tmp_path: Path):
    if pg_manager.async_engine is not None:
        await pg_manager.close()
    pg_manager.async_engine = None
    pg_manager.AsyncSession = None
    pg_manager._initialized = False
    monkeypatch.setenv("POSTGRES_URL", f"sqlite+aiosqlite:///{tmp_path / 'worldline-audit.db'}")
    pg_manager.initialize()
    await pg_manager.create_tables()
    try:
        yield pg_manager
    finally:
        await pg_manager.close()
        pg_manager.async_engine = None
        pg_manager.AsyncSession = None
        pg_manager._initialized = False


def _audit_run_payload() -> dict:
    return {
        "run": {
            "id": "run-audit-contract",
            "title": "Run Audit Contract",
            "goal": "Verify run inspector audit logging.",
        },
        "themeId": "agent-workbench",
        "rootQuestion": "Can run inspectors write MCP audit logs?",
        "branches": [
            {
                "id": "branch-audit",
                "title": "Audit branch",
                "branchType": "audit",
                "evidenceIds": ["ev-audit"],
                "toolCallIds": ["tool-audit"],
                "temporalFactIds": ["tf-audit"],
                "gateResultIds": ["gate-audit"],
                "score": 0.95,
            }
        ],
        "toolTraces": [
            {
                "id": "tool-audit",
                "branchId": "branch-audit",
                "name": "worldline.inspect_run_manifest",
                "status": "success",
                "permission": "worldline:read",
                "summary": "Inspect run manifest through service boundary.",
                "artifactIds": ["artifact-audit"],
            }
        ],
        "gateResults": [
            {
                "id": "gate-audit",
                "label": "Audit recorded",
                "status": "passed",
                "value": "1",
                "summary": "The read operation must leave an audit log.",
                "branchId": "branch-audit",
                "toolCallIds": ["tool-audit"],
                "artifactIds": ["artifact-audit"],
            }
        ],
        "evidenceRefs": [
            {
                "id": "ev-audit",
                "evidenceId": "ev-audit",
                "title": "Audit evidence",
                "summary": "MCP read inspection must be audited when audit_db_id is provided.",
                "sourceUri": "src/services/worldline_agent_workflow_service.py",
                "sourceRef": {
                    "id": "source-audit",
                    "label": "WorldlineAgentWorkflowService",
                    "documentNodeId": "node-audit",
                },
            }
        ],
        "wikiRefs": [
            {
                "id": "wiki-audit",
                "title": "Audit Wiki",
                "slug": "audit-wiki",
                "evidenceIds": ["ev-audit"],
            }
        ],
        "entityRefs": [
            {
                "id": "entity-audit",
                "name": "AuditLog",
                "type": "governance",
                "evidenceId": "ev-audit",
            }
        ],
        "timelineRefs": [
            {
                "id": "tf-audit",
                "label": "Run inspection writes an audit log",
                "validFrom": "2026-06-08",
                "status": "observed",
                "evidenceId": "ev-audit",
            }
        ],
    }


@pytest.mark.asyncio
async def test_run_inspectors_write_mcp_audit_logs(monkeypatch, tmp_path: Path, sqlite_pg_manager) -> None:
    audit_db_id = "kb_run_audit"
    monkeypatch.setattr("src.services.worldline_run_ledger_service.config.save_dir", str(tmp_path))

    async with pg_manager.get_async_session_context() as session:
        session.add(KnowledgeBase(db_id=audit_db_id, name="Run Audit KB", kb_type="codex_test"))

    ledger = WorldlineRunLedgerService()
    await ledger.create_run(_audit_run_payload(), created_by="tester")
    await ledger.register_artifact(
        "run-audit-contract",
        {
            "id": "artifact-audit",
            "label": "Audit artifact",
            "kind": "manifest_snapshot",
            "content": {"run": {"title": "Run Audit Contract"}},
        },
        actor="tester",
    )

    service = WorldlineAgentWorkflowService()
    results = [
        await service.inspect_run_manifest("run-audit-contract", audit_db_id=audit_db_id, actor="qa"),
        await service.inspect_run_artifacts(
            "run-audit-contract",
            artifact_id="artifact-audit",
            audit_db_id=audit_db_id,
            actor="qa",
        ),
        await service.inspect_run_gates(
            "run-audit-contract",
            gate_id="gate-audit",
            audit_db_id=audit_db_id,
            actor="qa",
        ),
        await service.inspect_run_evidence(
            "run-audit-contract",
            evidence_id="ev-audit",
            audit_db_id=audit_db_id,
            actor="qa",
        ),
        await service.inspect_run_knowledge(
            "run-audit-contract",
            kind="graph",
            item_id="entity-audit",
            audit_db_id=audit_db_id,
            actor="qa",
        ),
        await service.inspect_run_knowledge(
            "run-audit-contract",
            kind="wiki",
            item_id="missing-wiki",
            audit_db_id=audit_db_id,
            actor="qa",
        ),
    ]

    assert all(result["audit"]["recorded"] is True for result in results)
    assert results[-1]["status"] == "not_found"

    logs = await service.list_audit_logs(audit_db_id, limit=20)
    by_tool = {item["tool_name"]: item for item in logs["items"]}

    assert set(by_tool) == {
        "worldline.inspect_run_manifest",
        "worldline.inspect_run_artifacts",
        "worldline.inspect_run_gates",
        "worldline.inspect_run_evidence",
        "worldline.inspect_run_knowledge",
    }
    assert len(logs["items"]) == 6
    assert all(item["actor"] == "qa" for item in logs["items"])
    assert all(item["metadata"]["storage"] == "worldline_run_ledger" for item in logs["items"])
    assert by_tool["worldline.inspect_run_manifest"]["result_summary"]["section_count"] == 7
    assert by_tool["worldline.inspect_run_artifacts"]["request_summary"]["artifact_id"] == "artifact-audit"
    assert by_tool["worldline.inspect_run_gates"]["request_summary"]["gate_id"] == "gate-audit"
    assert by_tool["worldline.inspect_run_evidence"]["request_summary"]["evidence_id"] == "ev-audit"
    assert any(
        item["tool_name"] == "worldline.inspect_run_knowledge" and item["status"] == "not_found"
        for item in logs["items"]
    )
