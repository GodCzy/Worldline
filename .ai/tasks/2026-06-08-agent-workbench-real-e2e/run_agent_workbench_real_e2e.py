from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


API_BASE = os.getenv("WORLDLINE_E2E_API_BASE", "http://127.0.0.1:5050").rstrip("/")
ADMIN_LOGIN = os.getenv("WORLDLINE_E2E_ADMIN_LOGIN", "codex_temp_admin")
ADMIN_PASSWORD = os.getenv("WORLDLINE_E2E_ADMIN_PASSWORD", "")


def _request(
    method: str,
    path: str,
    *,
    token: str | None = None,
    json_body: dict[str, Any] | None = None,
    form_body: dict[str, str] | None = None,
    query: dict[str, Any] | None = None,
) -> dict[str, Any]:
    url = f"{API_BASE}{path}"
    if query:
        params = urllib.parse.urlencode({key: value for key, value in query.items() if value not in (None, "")})
        if params:
            url = f"{url}?{params}"

    headers: dict[str, str] = {}
    data: bytes | None = None
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if json_body is not None:
        data = json.dumps(json_body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if form_body is not None:
        data = urllib.parse.urlencode(form_body).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    request = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path} failed: status={exc.code} body={body}") from exc


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _run_payload(run_id: str) -> dict[str, Any]:
    return {
        "run": {
            "id": run_id,
            "title": f"Codex Agent Workbench E2E {run_id}",
            "goal": "Verify Agent Workbench against the durable run ledger API.",
            "budget": {"mode": "qa"},
        },
        "themeId": "agent-workbench",
        "rootQuestion": "Verify Agent Workbench against the durable run ledger API.",
        "branches": [
            {
                "id": "branch-plan",
                "title": "Planning branch",
                "branchType": "plan",
                "evidenceIds": ["ev-1"],
                "score": 0.9,
            },
            {
                "id": "branch-tool",
                "title": "Tool branch",
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
                        "path": f".ai/tasks/{run_id}/plan.json",
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


def main() -> int:
    if not ADMIN_PASSWORD:
        raise RuntimeError("WORLDLINE_E2E_ADMIN_PASSWORD is required")

    run_id = os.getenv("WORLDLINE_E2E_RUN_ID") or f"codex-e2e-agent-workbench-{int(time.time())}"

    login = _request(
        "POST",
        "/api/auth/token",
        form_body={"username": ADMIN_LOGIN, "password": ADMIN_PASSWORD},
    )
    token = str(login.get("access_token") or "")
    _expect(bool(token), "Login did not return access_token")
    _expect(login.get("role") in {"admin", "superadmin"}, f"Login role is not admin: {login.get('role')}")

    created = _request("POST", "/api/worldline/runs", token=token, json_body=_run_payload(run_id))
    _expect(created.get("id") == run_id, "Created run id mismatch")
    _expect(created.get("qualitySummary", {}).get("branchCount") == 2, "Created run branch count mismatch")

    approved = _request(
        "POST",
        f"/api/worldline/runs/{run_id}/branches/branch-tool/approve",
        token=token,
        json_body={"reason": "codex real API E2E approval"},
    )
    _expect(approved.get("activeBranchId") == "branch-tool", "Approved branch did not become active")

    rejected = _request(
        "POST",
        f"/api/worldline/runs/{run_id}/branches/branch-plan/reject",
        token=token,
        json_body={"reason": "codex real API E2E rejection"},
    )
    _expect(rejected.get("latestEvent", {}).get("eventType") == "branch.rejected", "Reject event missing")

    registered = _request(
        "POST",
        f"/api/worldline/runs/{run_id}/artifacts",
        token=token,
        json_body={
            "id": "e2e-replay-export",
            "kind": "replay_export",
            "format": "json+markdown",
            "label": "E2E Replay Export",
            "eventId": "evt-run-preview",
            "content": {
                "selectedEvent": {"id": "evt-run-preview", "eventType": "run.previewed", "label": "Run Preview"},
                "focusedDossier": {"title": "Codex Agent Workbench E2E"},
                "counts": {"artifacts": 1},
                "replayTimeline": [{"index": 1, "label": "Run Preview"}],
            },
            "markdown": "# E2E Replay Export\n\nRun: Codex Agent Workbench E2E",
        },
    )
    _expect(registered.get("artifact", {}).get("id") == "e2e-replay-export", "Artifact registration failed")

    detail = _request("GET", f"/api/worldline/runs/{run_id}", token=token)
    listed = _request(
        "GET",
        "/api/worldline/runs",
        token=token,
        query={"query": run_id, "status": "approved", "limit": 10},
    )
    events = _request("GET", f"/api/worldline/runs/{run_id}/events", token=token, query={"limit": 20})
    manifest = _request(
        "GET",
        f"/api/worldline/runs/{run_id}/manifest",
        token=token,
        query={"include_resources": "true", "limit": 10},
    )
    artifact_read = _request(
        "GET",
        f"/api/worldline/runs/{run_id}/artifacts/read",
        token=token,
        query={"artifact_id": "e2e-replay-export", "include_content": "true"},
    )
    gate_read = _request(
        "GET",
        f"/api/worldline/runs/{run_id}/gates",
        token=token,
        query={"gate_id": "gate-permission"},
    )
    evidence_read = _request(
        "GET",
        f"/api/worldline/runs/{run_id}/evidence",
        token=token,
        query={"source_id": "source-agent-workflow-service"},
    )
    knowledge_read = _request(
        "GET",
        f"/api/worldline/runs/{run_id}/knowledge",
        token=token,
        query={"kind": "graph", "item_id": "entity-worldline-run"},
    )

    _expect(detail.get("status") == "approved", "Run detail is not approved")
    _expect(listed.get("total") == 1, "Approved run list did not find the E2E run")
    _expect(events.get("total", 0) >= 4, "Run events did not include expected mutations")
    _expect(manifest.get("status") == "ok", "Run manifest status mismatch")
    _expect(manifest.get("resourceCounts", {}).get("artifacts") == 1, "Manifest artifact count mismatch")
    _expect(artifact_read.get("selected", {}).get("id") == "e2e-replay-export", "Artifact read mismatch")
    _expect(gate_read.get("selected", {}).get("id") == "gate-permission", "Gate read mismatch")
    _expect(evidence_read.get("selected", {}).get("evidenceId") == "ev-tool", "Evidence read mismatch")
    _expect(knowledge_read.get("selected", {}).get("id") == "entity-worldline-run", "Knowledge read mismatch")

    print(
        json.dumps(
            {
                "status": "ok",
                "api_base": API_BASE,
                "admin_login": ADMIN_LOGIN,
                "admin_role": login.get("role"),
                "run_id": run_id,
                "run_status": detail.get("status"),
                "event_total": events.get("total"),
                "manifest_resource_counts": manifest.get("resourceCounts"),
                "artifact_selected": artifact_read.get("selected", {}).get("id"),
                "gate_selected": gate_read.get("selected", {}).get("id"),
                "evidence_selected": evidence_read.get("selected", {}).get("evidenceId"),
                "knowledge_selected": knowledge_read.get("selected", {}).get("id"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
