from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from server.routers.worldline_run_router import worldline_runs
from server.utils.auth_middleware import get_admin_user
from src.services.worldline_agent_workflow_service import WorldlineAgentWorkflowService
from src.services.worldline_run_ledger_service import WorldlineRunLedgerService
from src.storage.postgres.models_business import User


def _run_payload() -> dict:
    return {
        "run": {
            "id": "run-stage2",
            "title": "Agent Workbench Stage 2",
            "goal": "Persist an Agent Worldline run.",
            "budget": {"mode": "stage_based"},
        },
        "themeId": "agent-workbench",
        "rootQuestion": "Persist an Agent Worldline run.",
        "branches": [
            {
                "id": "branch-plan",
                "title": "规划分支",
                "branchType": "plan",
                "evidenceIds": ["ev-1"],
                "score": 0.9,
            },
            {
                "id": "branch-tool",
                "title": "工具分支",
                "branchType": "tool_action",
                "toolCallIds": ["tool-1"],
                "evidenceIds": ["ev-tool"],
                "temporalFactIds": ["tf-tool"],
                "quality": {"status": "needs_approval"},
                "score": 0.8,
            },
        ],
        "episodes": [
            {
                "id": "episode-plan",
                "branchId": "branch-plan",
                "actor": "planner",
                "toolCalls": [],
                "gateResults": ["gate-evidence"],
            },
            {
                "id": "episode-tool",
                "branchId": "branch-tool",
                "actor": "executor",
                "toolCalls": ["tool-1"],
                "gateResults": ["gate-permission"],
                "artifactIds": ["artifact-tool-log"],
            },
        ],
        "toolTraces": [
            {
                "id": "tool-1",
                "branchId": "branch-tool",
                "name": "worldline.plan_workflow",
                "status": "approval_required",
                "permission": "worldline_service_boundary",
                "summary": "Plan controlled workflow steps.",
                "result": "Pending approval",
                "artifacts": [
                    {
                        "id": "artifact-plan",
                        "label": "Plan artifact",
                        "type": "json",
                        "path": ".ai/tasks/run-stage2/plan.json",
                        "summary": "Serialized workflow plan.",
                    }
                ],
            }
        ],
        "gateResults": [
            {
                "id": "gate-evidence",
                "label": "Evidence coverage",
                "status": "passed",
                "value": "90%",
                "threshold": ">= 80%",
                "toolCallIds": [],
                "artifactIds": ["artifact-plan"],
            },
            {
                "id": "gate-permission",
                "label": "Permission risk",
                "status": "review",
                "value": "1 approval",
                "threshold": "manual approval required",
                "input": "worldline_service_boundary",
                "toolCallIds": ["tool-1"],
                "artifactIds": ["artifact-tool-log"],
                "remediation": "Request operator approval before execution.",
            },
        ],
        "evidenceRefs": [
            {
                "id": "ev-1",
                "evidenceId": "ev-1",
                "title": "Planning contract",
                "type": "contract",
                "typeLabel": "EvidenceAnchor",
                "summary": "Planner branch must cite a concrete source.",
                "sourceUri": "docs/planning-contract.md",
                "lineStart": 10,
                "lineEnd": 18,
                "sourceRef": {
                    "id": "source-planning-contract",
                    "kind": "Markdown",
                    "label": "Planning contract source",
                    "documentNodeId": "docnode-planning-contract",
                    "documentNodeLabel": "Planning contract section",
                    "role": "Defines planning evidence requirements.",
                },
            },
            {
                "id": "ev-tool",
                "evidenceId": "ev-tool",
                "title": "Tool boundary evidence",
                "type": "service",
                "typeLabel": "EvidenceAnchor",
                "summary": "Tool branch must stay behind service boundaries.",
                "sourceUri": "src/services/worldline_agent_workflow_service.py",
                "lineStart": 20,
                "lineEnd": 44,
                "sourceRef": {
                    "id": "source-agent-workflow-service",
                    "kind": "Python service",
                    "label": "WorldlineAgentWorkflowService",
                    "documentNodeId": "docnode-agent-workflow-service",
                    "documentNodeLabel": "Agent workflow lanes",
                    "role": "Defines controlled tool write scopes.",
                },
            },
        ],
        "wikiRefs": [
            {
                "id": "wiki-agent-os",
                "title": "Agent Worldline OS",
                "slug": "agent-worldline-os",
                "status": "draft",
                "evidenceCoverage": 0.86,
                "summary": "A task is represented as a branching evidence-bound worldline.",
                "evidenceIds": ["ev-1", "ev-tool"],
            }
        ],
        "entityRefs": [
            {
                "id": "entity-worldline-run",
                "name": "WorldlineRun",
                "type": "agent_runtime",
                "confidence": 0.94,
                "evidenceId": "ev-1",
                "summary": "Run-level container for Agent worldline branches.",
            },
            {
                "id": "entity-tool-boundary",
                "name": "ToolBoundary",
                "type": "governance",
                "confidence": 0.9,
                "evidenceId": "ev-tool",
            },
        ],
        "timelineRefs": [
            {
                "id": "tf-tool",
                "label": "Tool execution remains behind service boundary",
                "validFrom": "2026-06-05",
                "validTo": "present",
                "status": "observed",
                "evidenceId": "ev-tool",
            }
        ],
        "skillProposals": [],
    }


@pytest.mark.asyncio
async def test_run_ledger_create_approve_reject_and_skill(tmp_path: Path) -> None:
    service = WorldlineRunLedgerService(storage_path=tmp_path / "runs.json")

    created = await service.create_run(_run_payload(), created_by="tester")

    assert created["id"] == "run-stage2"
    assert created["protocolVersion"] == "worldline-run-ledger-v0.1"
    assert created["qualitySummary"]["branchCount"] == 2
    assert created["events"][0]["eventType"] == "run.created"
    assert created["events"][0]["summary"]["evidenceIds"] == ["ev-1", "ev-tool"]
    assert created["events"][0]["summary"]["toolCallIds"] == ["tool-1"]
    assert created["events"][0]["summary"]["temporalFactIds"] == ["tf-tool"]
    assert created["events"][0]["summary"]["requiredPermissions"] == ["worldline_service_boundary"]
    assert created["events"][0]["summary"]["gateResultIds"] == ["gate-evidence", "gate-permission"]
    assert created["events"][0]["summary"]["artifactIds"] == ["artifact-plan"]
    assert created["events"][0]["summary"]["toolDetails"][0]["permission"] == "worldline_service_boundary"
    assert created["events"][0]["summary"]["gateDetails"][0]["label"] == "Evidence coverage"
    assert created["events"][0]["summary"]["artifactDetails"][0]["path"] == ".ai/tasks/run-stage2/plan.json"

    approved = await service.approve_branch("run-stage2", "branch-tool", {"reason": "safe"}, actor="tester")
    assert approved is not None
    assert approved["activeBranchId"] == "branch-tool"
    assert approved["latestEvent"]["eventType"] == "branch.approved"
    assert approved["latestEvent"]["summary"]["branch_title"] == "工具分支"
    assert approved["latestEvent"]["summary"]["evidenceIds"] == ["ev-tool"]
    assert approved["latestEvent"]["summary"]["toolCallIds"] == ["tool-1"]
    assert approved["latestEvent"]["summary"]["temporalFactIds"] == ["tf-tool"]
    assert approved["latestEvent"]["summary"]["requiredPermissions"] == ["worldline_service_boundary"]
    assert approved["latestEvent"]["summary"]["gateResultIds"] == ["gate-permission"]
    assert approved["latestEvent"]["summary"]["artifactIds"] == ["artifact-plan", "artifact-tool-log"]
    assert approved["latestEvent"]["summary"]["toolDetails"][0]["name"] == "worldline.plan_workflow"
    assert next(item for item in approved["branches"] if item["id"] == "branch-tool")["status"] == "approved"

    rejected = await service.reject_branch("run-stage2", "branch-plan", {"reason": "superseded"}, actor="tester")
    assert rejected is not None
    assert rejected["latestEvent"]["eventType"] == "branch.rejected"
    assert next(item for item in rejected["branches"] if item["id"] == "branch-plan")["decision"]["reason"] == "superseded"

    proposed = await service.propose_skill(
        "run-stage2",
        {
            "name": "Review Agent Ledger",
            "trigger": "run has approval queue",
            "steps": ["inspect branch", "approve or reject"],
            "requiredPermissions": ["worldline:read"],
            "evalScore": 0.82,
        },
        actor="tester",
    )
    assert proposed is not None
    assert proposed["skillProposal"]["id"] == "review-agent-ledger"
    assert proposed["qualitySummary"]["skillProposalCount"] == 1
    assert proposed["latestEvent"]["summary"]["requiredPermissions"] == ["worldline:read"]
    assert proposed["latestEvent"]["summary"]["evidenceRunIds"] == ["run-stage2"]
    assert proposed["latestEvent"]["summary"]["steps"] == ["inspect branch", "approve or reject"]

    registered = await service.register_artifact(
        "run-stage2",
        {
            "id": "replay-export-1",
            "kind": "replay_export",
            "format": "json+markdown",
            "label": "Replay Export",
            "eventId": "evt-run-preview",
            "content": {
                "selectedEvent": {"id": "evt-run-preview", "eventType": "run.previewed", "label": "Run Preview"},
                "focusedDossier": {"title": "Agent Workbench Stage 2"},
                "counts": {"artifacts": 1},
                "replayTimeline": [{"index": 1, "label": "Run Preview"}],
            },
            "markdown": "# Worldline Replay Export",
        },
        actor="tester",
    )
    assert registered is not None
    assert registered["artifact"]["id"] == "replay-export-1"
    assert registered["artifact"]["runId"] == "run-stage2"
    assert registered["latestEvent"]["eventType"] == "artifact.registered"
    assert registered["latestEvent"]["summary"]["artifactIds"] == ["replay-export-1"]
    assert registered["latestEvent"]["summary"]["artifactDetails"][0]["path"] == (
        "worldline-run-ledger://run-stage2/artifacts/replay-export-1"
    )
    assert registered["qualitySummary"]["artifactCount"] == 1

    artifacts = await service.list_artifacts("run-stage2")
    assert artifacts is not None
    assert artifacts["total"] == 1
    assert artifacts["items"][0]["markdown"] == "# Worldline Replay Export"

    gates = await service.list_gates("run-stage2")
    assert gates is not None
    assert gates["total"] == 2
    assert gates["items"][0]["threshold"] == ">= 80%"
    assert gates["items"][1]["toolCallIds"] == ["tool-1"]
    assert gates["items"][1]["artifactIds"] == ["artifact-tool-log"]

    evidence = await service.list_evidence("run-stage2")
    assert evidence is not None
    assert evidence["total"] == 2
    assert evidence["items"][0]["sourceUri"] == "docs/planning-contract.md"
    assert evidence["items"][0]["sourceRef"]["documentNodeId"] == "docnode-planning-contract"

    knowledge = await service.list_knowledge("run-stage2")
    assert knowledge is not None
    assert knowledge["total"] == 4
    assert [item["kind"] for item in knowledge["items"]] == ["wiki", "graph", "graph", "timeline"]

    graph = await service.list_knowledge("run-stage2", kind="graph")
    assert graph is not None
    assert graph["total"] == 2
    assert graph["items"][0]["name"] == "WorldlineRun"

    events = await service.list_events("run-stage2")
    assert events is not None
    assert [item["eventType"] for item in events["items"]] == [
        "run.created",
        "branch.approved",
        "branch.rejected",
        "skill.proposed",
        "artifact.registered",
    ]

    runs = await service.list_runs()
    assert runs["storage"] == {"type": "worldline_run_ledger", "read_only": True}
    assert runs["total"] == 1
    assert runs["filters"] == {"query": "", "status": "", "themeId": "", "createdBy": ""}
    assert runs["items"][0]["id"] == "run-stage2"
    assert runs["items"][0]["status"] == "approved"
    assert runs["items"][0]["rootQuestion"] == "Persist an Agent Worldline run."
    assert runs["items"][0]["counts"] == {
        "branches": 2,
        "episodes": 2,
        "tools": 1,
        "gates": 2,
        "artifacts": 1,
        "evidence": 2,
        "wiki": 1,
        "graph": 2,
        "timeline": 1,
        "skills": 1,
        "events": 5,
    }

    filtered_runs = await service.list_runs(query="persist", status="approved", theme_id="agent-workbench", created_by="tester")
    assert filtered_runs["total"] == 1
    assert filtered_runs["filters"] == {
        "query": "persist",
        "status": "approved",
        "themeId": "agent-workbench",
        "createdBy": "tester",
    }
    assert filtered_runs["items"][0]["id"] == "run-stage2"

    later_payload = _run_payload()
    later_payload["run"] = {
        **later_payload["run"],
        "id": "run-stage2-later",
        "title": "Later Agent Run",
    }
    later_payload["branches"] = [
        {
            **later_payload["branches"][0],
            "title": "Updated planning branch",
            "score": 0.95,
        },
        {
            "id": "branch-new",
            "title": "New evidence branch",
            "branchType": "evidence",
            "evidenceIds": ["ev-new"],
            "score": 0.7,
        },
    ]
    later_payload["episodes"] = later_payload["episodes"][:1]
    later_payload["toolTraces"] = []
    later_payload["gateResults"] = later_payload["gateResults"][:1]
    later_payload["evidenceRefs"] = later_payload["evidenceRefs"][:1]
    later_payload["wikiRefs"] = []
    later_payload["entityRefs"] = later_payload["entityRefs"][:1]
    later_payload["timelineRefs"] = []
    later_payload["skillProposals"] = []
    await service.create_run(later_payload, created_by="tester")

    compared = await service.compare_runs("run-stage2", "run-stage2-later")
    assert compared is not None
    assert compared["contractVersion"] == "worldline-run-compare-v0.1"
    assert compared["storage"] == {"type": "worldline_run_ledger", "read_only": True}
    assert compared["left"]["id"] == "run-stage2"
    assert compared["right"]["id"] == "run-stage2-later"
    assert compared["sections"]["branches"]["counts"]["added"] == 1
    assert compared["sections"]["branches"]["counts"]["removed"] == 1
    assert compared["sections"]["branches"]["counts"]["changed"] == 1
    assert compared["sections"]["branches"]["added"][0]["id"] == "branch-new"
    assert compared["sections"]["artifacts"]["counts"]["removed"] == 1
    assert compared["sections"]["tools"]["counts"]["removed"] == 1
    assert compared["sections"]["events"]["counts"]["added"] == 1
    assert compared["summary"]["sectionsChanged"] >= 5
    assert any(item["key"] == "branches" and item["totalDelta"] == 3 for item in compared["timeline"])
    assert await service.compare_runs("run-stage2", "missing-run") is None

    renamed = await service.rename_run("run-stage2", {"title": "Renamed Stage 2", "reason": "operator label"}, actor="tester")
    assert renamed is not None
    assert renamed["title"] == "Renamed Stage 2"
    assert renamed["latestEvent"]["eventType"] == "run.renamed"
    assert renamed["latestEvent"]["summary"] == {
        "oldTitle": "Agent Workbench Stage 2",
        "newTitle": "Renamed Stage 2",
        "reason": "operator label",
    }
    assert renamed["maintenance"]["lastRenamedBy"] == "tester"

    archived = await service.archive_run("run-stage2", {"reason": "completed"}, actor="tester")
    assert archived is not None
    assert archived["status"] == "archived"
    assert archived["archivedBy"] == "tester"
    assert archived["latestEvent"]["eventType"] == "run.archived"
    assert archived["latestEvent"]["summary"] == {
        "previousStatus": "approved",
        "status": "archived",
        "reason": "completed",
    }

    archived_runs = await service.list_runs(status="archived")
    assert archived_runs["total"] == 1
    assert archived_runs["items"][0]["id"] == "run-stage2"
    assert archived_runs["items"][0]["title"] == "Renamed Stage 2"
    restored = await service.restore_run("run-stage2", {"reason": "operator restored"}, actor="tester")
    assert restored is not None
    assert restored["status"] == "approved"
    assert "archivedAt" not in restored
    assert "archivedBy" not in restored
    assert restored["maintenance"]["lastRestoredBy"] == "tester"
    assert restored["maintenance"]["restoredFromStatus"] == "archived"
    assert restored["maintenance"]["restoredToStatus"] == "approved"
    assert restored["latestEvent"]["eventType"] == "run.restored"
    assert restored["latestEvent"]["summary"] == {
        "previousStatus": "archived",
        "status": "approved",
        "reason": "operator restored",
    }

    restored_approved_runs = await service.list_runs(status="approved")
    assert restored_approved_runs["total"] == 1
    assert restored_approved_runs["items"][0]["id"] == "run-stage2"
    restored_archived_runs = await service.list_runs(status="archived")
    assert restored_archived_runs["total"] == 0
    assert await service.rename_run("missing-run", {"title": "Missing"}, actor="tester") is None
    assert await service.archive_run("missing-run", {"reason": "missing"}, actor="tester") is None
    assert await service.restore_run("missing-run", {"reason": "missing"}, actor="tester") is None

    reloaded = await WorldlineRunLedgerService(storage_path=tmp_path / "runs.json").get_run("run-stage2")
    assert reloaded is not None
    assert reloaded["skillProposals"][0]["name"] == "Review Agent Ledger"
    assert reloaded["artifacts"][0]["id"] == "replay-export-1"
    assert reloaded["title"] == "Renamed Stage 2"
    assert reloaded["status"] == "approved"


def test_worldline_run_router_exposes_stage2_contract(monkeypatch, tmp_path: Path) -> None:
    app = FastAPI()
    app.include_router(worldline_runs, prefix="/api")

    async def fake_admin_user():
        return User(username="admin", user_id="admin", password_hash="x", role="admin")

    app.dependency_overrides[get_admin_user] = fake_admin_user
    monkeypatch.setattr("src.services.worldline_run_ledger_service.config.save_dir", str(tmp_path))

    client = TestClient(app)

    create_response = client.post("/api/worldline/runs", json=_run_payload())
    assert create_response.status_code == 200, create_response.text
    assert create_response.json()["id"] == "run-stage2"

    approve_response = client.post(
        "/api/worldline/runs/run-stage2/branches/branch-tool/approve",
        json={"reason": "validated"},
    )
    assert approve_response.status_code == 200, approve_response.text
    assert approve_response.json()["latestEvent"]["eventType"] == "branch.approved"

    skill_response = client.post(
        "/api/worldline/runs/run-stage2/skills/propose",
        json={"name": "Ledger Review", "steps": ["inspect"], "requiredPermissions": ["worldline:read"]},
    )
    assert skill_response.status_code == 200, skill_response.text
    assert skill_response.json()["skillProposal"]["name"] == "Ledger Review"

    artifact_response = client.post(
        "/api/worldline/runs/run-stage2/artifacts",
        json={
            "id": "router-replay-export",
            "label": "Router Replay Export",
            "content": {"replayTimeline": [{"index": 1, "label": "Run Preview"}]},
            "markdown": "# Router Replay Export",
        },
    )
    assert artifact_response.status_code == 200, artifact_response.text
    assert artifact_response.json()["artifact"]["id"] == "router-replay-export"
    assert artifact_response.json()["latestEvent"]["eventType"] == "artifact.registered"

    artifacts_response = client.get("/api/worldline/runs/run-stage2/artifacts")
    assert artifacts_response.status_code == 200, artifacts_response.text
    assert artifacts_response.json()["total"] == 1
    assert artifacts_response.json()["items"][0]["label"] == "Router Replay Export"

    second_payload = _run_payload()
    second_payload["run"] = {
        **second_payload["run"],
        "id": "run-stage2-later",
        "title": "Later Agent Run",
    }
    second_payload["rootQuestion"] = "Load a later Agent Worldline run."
    second_response = client.post("/api/worldline/runs", json=second_payload)
    assert second_response.status_code == 200, second_response.text

    runs_response = client.get("/api/worldline/runs?limit=10")
    assert runs_response.status_code == 200, runs_response.text
    runs = runs_response.json()
    assert runs["storage"] == {"type": "worldline_run_ledger", "read_only": True}
    assert runs["total"] == 2
    assert runs["filters"] == {"query": "", "status": "", "themeId": "", "createdBy": ""}
    assert runs["items"][0]["id"] == "run-stage2-later"
    assert runs["items"][0]["title"] == "Later Agent Run"
    stage2_summary = next(item for item in runs["items"] if item["id"] == "run-stage2")
    assert stage2_summary["counts"] == {
        "branches": 2,
        "episodes": 2,
        "tools": 1,
        "gates": 2,
        "artifacts": 1,
        "evidence": 2,
        "wiki": 1,
        "graph": 2,
        "timeline": 1,
        "skills": 1,
        "events": 4,
    }

    filtered_response = client.get(
        "/api/worldline/runs?limit=10&query=later&status=ready&theme_id=agent-workbench&created_by=admin"
    )
    assert filtered_response.status_code == 200, filtered_response.text
    filtered = filtered_response.json()
    assert filtered["total"] == 1
    assert filtered["filters"] == {
        "query": "later",
        "status": "ready",
        "themeId": "agent-workbench",
        "createdBy": "admin",
    }
    assert filtered["items"][0]["id"] == "run-stage2-later"

    approved_response = client.get("/api/worldline/runs?query=persist&status=approved&limit=10")
    assert approved_response.status_code == 200, approved_response.text
    approved_runs = approved_response.json()
    assert approved_runs["total"] == 1
    assert approved_runs["items"][0]["id"] == "run-stage2"

    paginated_response = client.get("/api/worldline/runs?limit=1&offset=1")
    assert paginated_response.status_code == 200, paginated_response.text
    paginated = paginated_response.json()
    assert paginated["total"] == 2
    assert paginated["limit"] == 1
    assert paginated["offset"] == 1
    assert len(paginated["items"]) == 1

    compare_response = client.get("/api/worldline/runs/compare?left_run_id=run-stage2&right_run_id=run-stage2-later")
    assert compare_response.status_code == 200, compare_response.text
    compare = compare_response.json()
    assert compare["contractVersion"] == "worldline-run-compare-v0.1"
    assert compare["left"]["id"] == "run-stage2"
    assert compare["right"]["id"] == "run-stage2-later"
    assert compare["sections"]["artifacts"]["counts"]["removed"] == 1
    assert compare["sections"]["events"]["counts"]["added"] == 1
    assert any(item["key"] == "artifacts" for item in compare["timeline"])

    missing_compare = client.get("/api/worldline/runs/compare?left_run_id=run-stage2&right_run_id=missing-run")
    assert missing_compare.status_code == 404
    assert "run-stage2/missing-run" in missing_compare.json()["detail"]

    rename_response = client.post(
        "/api/worldline/runs/run-stage2/rename",
        json={"title": "Router Renamed Run", "reason": "operator cleanup"},
    )
    assert rename_response.status_code == 200, rename_response.text
    renamed = rename_response.json()
    assert renamed["title"] == "Router Renamed Run"
    assert renamed["latestEvent"]["eventType"] == "run.renamed"
    assert renamed["latestEvent"]["summary"]["oldTitle"] == "Agent Workbench Stage 2"
    assert renamed["latestEvent"]["summary"]["newTitle"] == "Router Renamed Run"

    empty_rename = client.post("/api/worldline/runs/run-stage2/rename", json={"title": "   "})
    assert empty_rename.status_code == 400

    archive_response = client.post(
        "/api/worldline/runs/run-stage2/archive",
        json={"reason": "operator archived"},
    )
    assert archive_response.status_code == 200, archive_response.text
    archived = archive_response.json()
    assert archived["status"] == "archived"
    assert archived["archivedBy"] == "admin"
    assert archived["latestEvent"]["eventType"] == "run.archived"
    assert archived["latestEvent"]["summary"]["previousStatus"] == "approved"

    archived_list_response = client.get("/api/worldline/runs?status=archived&limit=10")
    assert archived_list_response.status_code == 200, archived_list_response.text
    archived_list = archived_list_response.json()
    assert archived_list["total"] == 1
    assert archived_list["items"][0]["id"] == "run-stage2"
    assert archived_list["items"][0]["title"] == "Router Renamed Run"

    restore_response = client.post(
        "/api/worldline/runs/run-stage2/restore",
        json={"reason": "operator restored"},
    )
    assert restore_response.status_code == 200, restore_response.text
    restored = restore_response.json()
    assert restored["status"] == "approved"
    assert "archivedAt" not in restored
    assert "archivedBy" not in restored
    assert restored["latestEvent"]["eventType"] == "run.restored"
    assert restored["latestEvent"]["summary"]["previousStatus"] == "archived"
    assert restored["latestEvent"]["summary"]["status"] == "approved"

    restored_archived_list_response = client.get("/api/worldline/runs?status=archived&limit=10")
    assert restored_archived_list_response.status_code == 200, restored_archived_list_response.text
    assert restored_archived_list_response.json()["total"] == 0

    restored_approved_list_response = client.get("/api/worldline/runs?status=approved&limit=10")
    assert restored_approved_list_response.status_code == 200, restored_approved_list_response.text
    restored_approved_list = restored_approved_list_response.json()
    assert restored_approved_list["total"] == 1
    assert restored_approved_list["items"][0]["id"] == "run-stage2"

    missing_rename = client.post("/api/worldline/runs/missing-run/rename", json={"title": "Missing"})
    assert missing_rename.status_code == 404
    missing_archive = client.post("/api/worldline/runs/missing-run/archive", json={"reason": "missing"})
    assert missing_archive.status_code == 404
    missing_restore = client.post("/api/worldline/runs/missing-run/restore", json={"reason": "missing"})
    assert missing_restore.status_code == 404

    manifest_response = client.get("/api/worldline/runs/run-stage2/manifest?include_resources=true&limit=10")
    assert manifest_response.status_code == 200, manifest_response.text
    manifest = manifest_response.json()
    assert manifest["contractVersion"] == "worldline-run-mcp-manifest-v0.1"
    assert manifest["status"] == "ok"
    assert manifest["run"]["id"] == "run-stage2"
    assert manifest["storage"] == {"type": "worldline_run_ledger", "read_only": True}
    assert manifest["resourceCounts"] == {
        "artifacts": 1,
        "gates": 2,
        "evidence": 2,
        "sources": 2,
        "wiki": 1,
        "graph": 2,
        "timeline": 1,
    }
    assert manifest["sections"]["artifacts"]["resources"][0]["args"]["artifact_id"] == "router-replay-export"
    assert manifest["sections"]["wiki"]["resources"][0]["args"] == {
        "run_id": "run-stage2",
        "kind": "wiki",
        "item_id": "wiki-agent-os",
        "audit_db_id": "",
    }
    assert any(tool["name"] == "worldline.inspect_run_manifest" for tool in manifest["tools"])

    artifact_read_response = client.get(
        "/api/worldline/runs/run-stage2/artifacts/read?artifact_id=router-replay-export&include_content=true"
    )
    assert artifact_read_response.status_code == 200, artifact_read_response.text
    artifact_read = artifact_read_response.json()
    assert artifact_read["status"] == "ok"
    assert artifact_read["selected"]["id"] == "router-replay-export"
    assert artifact_read["selected"]["content"]["replayTimeline"][0]["label"] == "Run Preview"

    gate_read_response = client.get("/api/worldline/runs/run-stage2/gates?gate_id=gate-permission")
    assert gate_read_response.status_code == 200, gate_read_response.text
    gate_read = gate_read_response.json()
    assert gate_read["selected"]["id"] == "gate-permission"
    assert gate_read["selected"]["toolCallIds"] == ["tool-1"]

    evidence_read_response = client.get("/api/worldline/runs/run-stage2/evidence?source_id=source-agent-workflow-service")
    assert evidence_read_response.status_code == 200, evidence_read_response.text
    evidence_read = evidence_read_response.json()
    assert evidence_read["selected"]["evidenceId"] == "ev-tool"
    assert evidence_read["selected"]["sourceRef"]["label"] == "WorldlineAgentWorkflowService"

    knowledge_read_response = client.get("/api/worldline/runs/run-stage2/knowledge?kind=graph&item_id=entity-worldline-run")
    assert knowledge_read_response.status_code == 200, knowledge_read_response.text
    knowledge_read = knowledge_read_response.json()
    assert knowledge_read["selected"]["id"] == "entity-worldline-run"
    assert knowledge_read["selected"]["uri"] == "worldline-run-ledger://run-stage2/graph/entity-worldline-run"

    missing_resource_response = client.get("/api/worldline/runs/run-stage2/knowledge?kind=wiki&item_id=missing-wiki")
    assert missing_resource_response.status_code == 404
    assert "missing-wiki" in missing_resource_response.json()["detail"]

    missing_manifest_response = client.get("/api/worldline/runs/missing-run/manifest")
    assert missing_manifest_response.status_code == 404
    assert "missing-run" in missing_manifest_response.json()["detail"]

    events_response = client.get("/api/worldline/runs/run-stage2/events")
    assert events_response.status_code == 200, events_response.text
    event_body = events_response.json()
    assert event_body["total"] == 7
    assert [event["eventType"] for event in event_body["items"][-3:]] == [
        "run.renamed",
        "run.archived",
        "run.restored",
    ]


@pytest.mark.asyncio
async def test_worldline_mcp_can_read_run_replay_artifacts(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("src.services.worldline_run_ledger_service.config.save_dir", str(tmp_path))
    ledger = WorldlineRunLedgerService()
    await ledger.create_run(_run_payload(), created_by="tester")
    await ledger.register_artifact(
        "run-stage2",
        {
            "id": "mcp-replay-export",
            "label": "MCP Replay Export",
            "content": {
                "protocol": "worldline-agent-workbench-v0.1",
                "run": {"title": "Agent Workbench Stage 2"},
                "selectedEvent": {"label": "Run Preview"},
                "focusedDossier": {"title": "Agent Workbench Stage 2"},
                "replayTimeline": [{"index": 1, "label": "Run Preview"}],
                "counts": {"artifacts": 1},
            },
            "markdown": "# MCP Replay Export\n\nRun: Agent Workbench Stage 2",
        },
        actor="tester",
    )

    service = WorldlineAgentWorkflowService()
    result = await service.inspect_run_artifacts("run-stage2", include_content=False)

    assert result["status"] == "ok"
    assert result["storage"]["read_only"] is True
    assert result["audit"] == {"recorded": False, "reason": "audit_db_id_not_provided"}
    assert result["items"][0]["id"] == "mcp-replay-export"
    assert result["items"][0]["uri"] == "worldline-run-ledger://run-stage2/artifacts/mcp-replay-export"
    assert result["items"][0]["content_summary"]["run_title"] == "Agent Workbench Stage 2"
    assert "content" not in result["items"][0]
    assert "markdown" not in result["items"][0]

    selected = await service.inspect_run_artifacts(
        "run-stage2",
        artifact_id="mcp-replay-export",
        include_content=True,
    )

    assert selected["status"] == "ok"
    assert selected["selected"]["content"]["protocol"] == "worldline-agent-workbench-v0.1"
    assert selected["selected"]["markdown"].startswith("# MCP Replay Export")


@pytest.mark.asyncio
async def test_worldline_mcp_can_read_run_gate_results(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("src.services.worldline_run_ledger_service.config.save_dir", str(tmp_path))
    ledger = WorldlineRunLedgerService()
    await ledger.create_run(_run_payload(), created_by="tester")

    service = WorldlineAgentWorkflowService()
    result = await service.inspect_run_gates("run-stage2")

    assert result["status"] == "ok"
    assert result["storage"]["read_only"] is True
    assert result["audit"] == {"recorded": False, "reason": "audit_db_id_not_provided"}
    assert result["total"] == 2
    assert result["items"][0]["id"] == "gate-evidence"
    assert result["items"][0]["uri"] == "worldline-run-ledger://run-stage2/gates/gate-evidence"
    assert result["items"][0]["threshold"] == ">= 80%"

    selected = await service.inspect_run_gates("run-stage2", gate_id="gate-permission")

    assert selected["status"] == "ok"
    assert selected["selected"]["label"] == "Permission risk"
    assert selected["selected"]["toolCallIds"] == ["tool-1"]
    assert selected["selected"]["artifactIds"] == ["artifact-tool-log"]
    assert selected["selected"]["remediation"] == "Request operator approval before execution."

    missing = await service.inspect_run_gates("run-stage2", gate_id="missing-gate")
    assert missing["status"] == "not_found"
    assert missing["items"] == []


@pytest.mark.asyncio
async def test_worldline_mcp_can_read_run_evidence_and_sources(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("src.services.worldline_run_ledger_service.config.save_dir", str(tmp_path))
    ledger = WorldlineRunLedgerService()
    await ledger.create_run(_run_payload(), created_by="tester")

    service = WorldlineAgentWorkflowService()
    result = await service.inspect_run_evidence("run-stage2")

    assert result["status"] == "ok"
    assert result["storage"]["read_only"] is True
    assert result["audit"] == {"recorded": False, "reason": "audit_db_id_not_provided"}
    assert result["total"] == 2
    assert result["items"][0]["evidenceId"] == "ev-1"
    assert result["items"][0]["uri"] == "worldline-run-ledger://run-stage2/evidence/ev-1"
    assert result["items"][0]["sourceUriRef"] == "worldline-run-ledger://run-stage2/sources/source-planning-contract"
    assert result["items"][0]["documentNode"]["id"] == "docnode-planning-contract"

    selected = await service.inspect_run_evidence("run-stage2", evidence_id="ev-tool")

    assert selected["status"] == "ok"
    assert selected["selected"]["title"] == "Tool boundary evidence"
    assert selected["selected"]["sourceRef"]["id"] == "source-agent-workflow-service"
    assert selected["selected"]["lineStart"] == 20

    source_selected = await service.inspect_run_evidence(
        "run-stage2",
        source_id="source-agent-workflow-service",
    )

    assert source_selected["status"] == "ok"
    assert source_selected["selected"]["evidenceId"] == "ev-tool"
    assert source_selected["selected"]["sourceUri"] == "src/services/worldline_agent_workflow_service.py"

    missing = await service.inspect_run_evidence("run-stage2", source_id="missing-source")
    assert missing["status"] == "not_found"
    assert missing["items"] == []


@pytest.mark.asyncio
async def test_worldline_mcp_can_read_run_knowledge_refs(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("src.services.worldline_run_ledger_service.config.save_dir", str(tmp_path))
    ledger = WorldlineRunLedgerService()
    await ledger.create_run(_run_payload(), created_by="tester")

    service = WorldlineAgentWorkflowService()
    result = await service.inspect_run_knowledge("run-stage2")

    assert result["status"] == "ok"
    assert result["storage"]["read_only"] is True
    assert result["audit"] == {"recorded": False, "reason": "audit_db_id_not_provided"}
    assert result["total"] == 4
    assert result["items"][0]["kind"] == "wiki"
    assert result["items"][0]["uri"] == "worldline-run-ledger://run-stage2/wiki/wiki-agent-os"
    assert result["items"][0]["evidenceIds"] == ["ev-1", "ev-tool"]

    graph = await service.inspect_run_knowledge("run-stage2", kind="graph", item_id="entity-worldline-run")

    assert graph["status"] == "ok"
    assert graph["selected"]["name"] == "WorldlineRun"
    assert graph["selected"]["evidenceId"] == "ev-1"
    assert graph["selected"]["uri"] == "worldline-run-ledger://run-stage2/graph/entity-worldline-run"

    timeline = await service.inspect_run_knowledge("run-stage2", kind="timeline", item_id="tf-tool")

    assert timeline["status"] == "ok"
    assert timeline["selected"]["label"] == "Tool execution remains behind service boundary"
    assert timeline["selected"]["validFrom"] == "2026-06-05"

    missing = await service.inspect_run_knowledge("run-stage2", kind="wiki", item_id="missing-wiki")
    assert missing["status"] == "not_found"
    assert missing["items"] == []


@pytest.mark.asyncio
async def test_worldline_mcp_can_read_run_manifest(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("src.services.worldline_run_ledger_service.config.save_dir", str(tmp_path))
    ledger = WorldlineRunLedgerService()
    await ledger.create_run(_run_payload(), created_by="tester")
    await ledger.register_artifact(
        "run-stage2",
        {
            "id": "manifest-replay-export",
            "label": "Manifest Replay Export",
            "content": {"run": {"title": "Agent Workbench Stage 2"}},
        },
        actor="tester",
    )

    service = WorldlineAgentWorkflowService()
    result = await service.inspect_run_manifest("run-stage2")

    assert result["status"] == "ok"
    assert result["contractVersion"] == "worldline-run-mcp-manifest-v0.1"
    assert result["storage"]["read_only"] is True
    assert result["audit"] == {"recorded": False, "reason": "audit_db_id_not_provided"}
    assert result["run"]["uri"] == "worldline-run-ledger://run-stage2"
    assert set(result["sections"]) == {"artifacts", "gates", "evidence", "sources", "wiki", "graph", "timeline"}
    assert result["resourceCounts"]["artifacts"] == 1
    assert result["resourceCounts"]["gates"] == 2
    assert result["resourceCounts"]["evidence"] == 2
    assert result["resourceCounts"]["sources"] == 2
    assert result["resourceCounts"]["wiki"] == 1
    assert result["resourceCounts"]["graph"] == 2
    assert result["resourceCounts"]["timeline"] == 1
    assert result["sections"]["artifacts"]["resources"][0]["tool"] == "worldline.inspect_run_artifacts"
    assert result["sections"]["artifacts"]["resources"][0]["args"]["artifact_id"] == "manifest-replay-export"
    assert result["sections"]["sources"]["resources"][0]["args"]["source_id"] == "source-planning-contract"
    assert result["sections"]["wiki"]["resources"][0]["args"]["kind"] == "wiki"
    assert result["sections"]["graph"]["resources"][0]["uri"] == "worldline-run-ledger://run-stage2/graph/entity-worldline-run"
    assert result["sections"]["timeline"]["resources"][0]["args"]["item_id"] == "tf-tool"

    compact = await service.inspect_run_manifest("run-stage2", include_resources=False)
    assert compact["status"] == "ok"
    assert compact["sections"]["gates"]["count"] == 2
    assert compact["sections"]["gates"]["resources"] == []

    missing = await service.inspect_run_manifest("missing-run")
    assert missing["status"] == "not_found"
    assert missing["sections"] == {}
