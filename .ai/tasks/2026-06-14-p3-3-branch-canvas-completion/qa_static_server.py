from __future__ import annotations

import argparse
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


def branch_payload() -> dict:
    evidence_refs = [
        {
            "id": "ev-p3-3-route",
            "evidenceId": "ev-p3-3-route",
            "title": "P3-3 Branch Canvas Contract",
            "typeLabel": "EvidenceAnchor",
            "summary": "Branch payloads must expose evidence, wiki, graph, timeline, gate refs, and route trace.",
            "sourceUri": "docs/product/worldline-next-roadmap.md",
            "page": 1,
            "lineStart": 98,
            "lineEnd": 118,
        },
        {
            "id": "ev-p3-3-mobile",
            "evidenceId": "ev-p3-3-mobile",
            "title": "Mobile QA Requirement",
            "typeLabel": "EvidenceAnchor",
            "summary": "390x844 must avoid page-level horizontal overflow while keeping the canvas inspectable.",
            "sourceUri": "docs/architecture/evaluation-gates.md",
            "lineStart": 34,
        },
    ]
    wiki_refs = [
        {
            "id": "wiki-branch-canvas",
            "title": "Worldline Branch Canvas",
            "slug": "worldline-branch-canvas",
            "status": "reviewed",
            "evidenceCoverage": 0.92,
        }
    ]
    entity_refs = [
        {
            "id": "entity-worldline-branch",
            "name": "Worldline Branch",
            "type": "concept",
            "confidence": 0.93,
            "evidenceId": "ev-p3-3-route",
        }
    ]
    timeline_refs = [
        {
            "id": "fact-p3-3-completion",
            "label": "P3-3 branch trace completed",
            "validFrom": "2026-06-14",
            "status": "observed",
            "evidenceId": "ev-p3-3-mobile",
        }
    ]
    gate_refs = [
        {
            "id": "gate-p3-3-qa",
            "gateId": "gate-p3-3-qa",
            "status": "passed",
            "failureCount": 0,
            "summary": "P3-3 QA gate fixture",
        }
    ]

    branches = []
    for index, branch_id in enumerate(("live-evidence", "live-wiki", "live-graph-timeline")):
        choice = ("Evidence", "Wiki", "Graph/Timeline")[index]
        branch = {
            "id": branch_id,
            "title": ("Evidence-first branch", "LLM Wiki branch", "Graph and timeline branch")[index],
            "subtitle": ("Confirm EvidenceAnchor before generating", "Enter through the Wiki surface", "Inspect entities, relations, and facts")[index],
            "summary": f"{choice} branch is backed by evidence, wiki, entity, timeline, and gate refs.",
            "branchTone": choice,
            "riskLabel": "Verifiable",
            "costLabel": "Low impact",
            "confidenceLabel": "Backend evidence baseline",
            "routeTone": "Keep source, graph, and quality gate traceable before deeper generation.",
            "tone": ("calm", "focus", "peak")[index],
            "choiceLabel": choice,
            "suitability": ["live backend", "evidence first", "replayable"],
            "focus": branch_id,
            "choiceReason": "This branch comes from persisted Worldline knowledge objects, not a static adapter sample.",
            "switchHint": "If evidence is thin, rebuild Wiki/Graph or rerun quality gates before continuing.",
            "evidenceRefs": evidence_refs,
            "wikiRefs": wiki_refs,
            "entityRefs": entity_refs,
            "timelineRefs": timeline_refs,
            "gateRefs": gate_refs,
            "quality": {
                "status": "passed",
                "evidenceCount": len(evidence_refs),
                "supportChannels": 4,
                "citationCoverage": 0.92,
                "graphSupport": True,
                "temporalSupport": True,
                "gateStatus": "passed",
                "gateCount": 1,
                "hints": [],
            },
            "routeTrace": {
                "db_id": "kb_p3_branch",
                "theme_id": "p3-branch",
                "branch_id": branch_id,
                "facade": "WorldlineWorkbenchService",
                "branchMode": choice,
                "sourceType": "worldline-live-facade-v1",
                "conclusionPolicy": "evidence_required",
                "supportStatus": "passed",
                "insufficientEvidence": False,
                "counts": {"evidence": 2, "wiki": 1, "entity": 1, "timeline": 1, "gate": 1},
                "path": [
                    "root_question",
                    "branch_canvas",
                    "branch_inspector",
                    "evidence_rail",
                    "timeline_scrubber",
                    "graph_focus",
                    "quality_gate",
                ],
                "hints": [],
            },
            "nextStepTitle": "Continue branch validation",
            "nextStepSubtitle": "Take this branch into Agent, Graph, or Quality Gate checks.",
            "nextGenerationLabel": "Continue from live knowledge",
            "nextActions": [
                {
                    "id": f"{branch_id}-chat",
                    "label": "Open branch chat",
                    "description": "Send live knowledge context to the Agent.",
                    "targetType": "chat",
                    "emphasis": "primary",
                },
                {
                    "id": f"{branch_id}-graph",
                    "label": "Inspect graph support",
                    "description": "Open the graph page to inspect entities, relations, and timeline facts.",
                    "targetType": "graph",
                    "emphasis": "secondary",
                },
            ],
            "context": {
                "theme": "p3-branch",
                "module": "p3-branch",
                "db_id": "kb_p3_branch",
                "knowledge_db_id": "kb_p3_branch",
                "focus": branch_id,
                "branch": branch_id,
            },
        }
        branches.append(branch)

    nodes = [
        {"id": "root-question", "type": "root", "title": "Root question", "subtitle": "P3 Branch Canvas QA", "meta": "Live Query", "x": 120, "y": 280, "radius": 10},
    ]
    edges = []
    for index, branch in enumerate(branches):
        y = 140 + index * 160
        nodes.extend(
            [
                {"id": branch["id"], "type": "branch", "title": branch["title"], "subtitle": branch["subtitle"], "meta": f"{branch['choiceLabel']} / {branch['confidenceLabel']}", "x": 420, "y": y, "radius": 9, "branchId": branch["id"], "tone": branch["tone"]},
                {"id": f"{branch['id']}-next", "type": "next-step", "title": "Continue validation", "subtitle": branch["nextStepSubtitle"], "meta": "Agent / Graph / Gate", "x": 760, "y": y, "radius": 8, "branchId": branch["id"], "tone": branch["tone"]},
            ]
        )
        edges.extend(
            [
                {"id": f"edge-root-{branch['id']}", "source": "root-question", "target": branch["id"], "branchId": branch["id"], "kind": "primary" if index == 0 else "secondary", "label": branch["choiceLabel"], "isHighlighted": index == 0},
                {"id": f"edge-next-{branch['id']}", "source": branch["id"], "target": f"{branch['id']}-next", "branchId": branch["id"], "kind": "guide", "label": "Continue", "isHighlighted": index == 0},
            ]
        )
    nodes.append({"id": "convergence", "type": "convergence", "title": "Converged validation", "subtitle": "Evidence, graph, and quality gate", "meta": "Evidence OS", "x": 1010, "y": 280, "radius": 11, "branchId": "live-evidence", "tone": "peak"})
    for index, branch in enumerate(branches):
        edges.append({"id": f"edge-converge-{branch['id']}", "source": f"{branch['id']}-next", "target": "convergence", "branchId": branch["id"], "kind": "convergence", "label": "Gate convergence", "isHighlighted": index == 0})

    return {
        "themeId": "p3-branch",
        "moduleId": "p3-branch",
        "knowledgeDbId": "kb_p3_branch",
        "knowledgeMode": "llm_wiki_primary_rag_auxiliary",
        "layers": ["evidence_ledger", "llm_wiki", "temporal_evidence_graph", "quality_gate", "agent_handoff"],
        "rootQuestion": "P3 Branch Canvas QA",
        "questionDraft": "P3 Branch Canvas QA",
        "status": "ready",
        "sourceType": "worldline-live-facade-v1",
        "generationMode": "base",
        "generationRound": 1,
        "branches": branches,
        "activeBranchId": branches[0]["id"],
        "selectedNodeId": branches[0]["id"],
        "tree": {"width": 1160, "height": 700, "nodes": nodes, "edges": edges},
        "viewState": {"lastGeneratedFrom": "live-generate", "protocolVersion": "worldline-live-v1"},
        "displayMeta": {
            "stageLabel": "Live knowledge",
            "stageTitle": "Generate branches from evidence, Wiki, graph, and timeline",
            "stageSubtitle": "P3-3 QA fixture for branch route trace, gate refs, and mobile containment.",
            "branchCount": len(branches),
            "themeName": "P3 Branch Canvas QA",
            "generationLabel": "Generate live branches",
            "generationMode": "base",
            "workspaceHint": "Inspect evidence support, then take the branch into Agent, Graph, or Quality Gate validation.",
        },
        "snapshots": [
            {"id": "source", "label": "Source", "title": "Evidence ledger", "metric": 2, "summary": "EvidenceAnchor coverage"},
            {"id": "wiki", "label": "Wiki", "title": "LLM Wiki rebuild", "metric": 1, "summary": "Wiki refs"},
            {"id": "graph", "label": "Graph", "title": "Temporal graph projection", "metric": 2, "summary": "Graph and timeline refs"},
            {"id": "gate", "label": "Gate", "title": "Quality gate", "metric": 1, "summary": "Latest gate passed"},
        ],
        "quality": {
            "status": "passed",
            "gateId": "gate-p3-3-qa",
            "branchCount": len(branches),
            "citationCoverage": 0.92,
            "latestGate": {"gate_id": "gate-p3-3-qa", "status": "passed", "failure_replay": []},
            "supportStatus": "inspectable",
            "hints": [],
        },
        "routeTrace": {
            "db_id": "kb_p3_branch",
            "facade": "WorldlineWorkbenchService",
            "deterministic_baseline": True,
            "conclusion_policy": "evidence_required",
            "evidence_required": True,
            "support_status": "inspectable",
            "supportStatus": "inspectable",
            "counts": {"evidence_anchors": 2, "wiki_pages": 1, "entities": 1, "temporal_facts": 1},
            "evidence_count": 2,
            "wiki_page_count": 1,
            "entity_count": 1,
            "timeline_count": 1,
            "quality_gate_status": "passed",
        },
        "overview": {"status": "ready", "counts": {"evidence_anchors": 2, "wiki_pages": 1, "entities": 1, "temporal_facts": 1}, "quality_gate": {"latest": {"gate_id": "gate-p3-3-qa", "status": "passed"}}},
    }


def info_payload() -> dict:
    return {
        "success": True,
        "data": {
            "organization": {"name": "Worldline", "logo": "/favicon.svg", "avatar": "/avatar.jpg"},
            "branding": {"name": "Worldline", "title": "Worldline", "subtitle": "P3 Branch Canvas QA"},
            "features": [],
            "themes": [
                {
                    "id": "p3-branch",
                    "name": "P3 Branch Canvas QA",
                    "subtitle": "Evidence-bound branch canvas",
                    "description": "QA fixture for P3-3 routeTrace, gate refs, and mobile containment.",
                    "featured": True,
                    "worldline": {"knowledge_db_id": "kb_p3_branch", "default_question": "P3 Branch Canvas QA"},
                    "context": {"knowledge_db_id": "kb_p3_branch", "scene": "worldline"},
                }
            ],
            "actions": [],
            "footer": {"copyright": "Worldline 2026"},
        },
    }


class QAHandler(SimpleHTTPRequestHandler):
    dist_root: Path

    def _send_json(self, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        if self.path.endswith("/worldline/generate"):
            length = int(self.headers.get("Content-Length") or "0")
            if length:
                self.rfile.read(length)
            self._send_json(branch_payload())
            return
        self._send_json({"status": "ok"})

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/seed":
            target = parse_qs(parsed.query).get("target", ["/worldline/p3-branch"])[0]
            body = f"""
<!doctype html>
<meta charset="utf-8">
<script>
localStorage.setItem('user_token', 'qa-token');
location.replace({json.dumps(target)});
</script>
""".encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path == "/api/auth/me":
            self._send_json({"id": "qa-admin", "username": "qa-admin", "user_id": "qa-admin", "role": "admin"})
            return
        if parsed.path == "/api/system/info":
            self._send_json(info_payload())
            return
        if parsed.path.endswith("/worldline/overview"):
            payload = branch_payload()["overview"]
            self._send_json(payload)
            return

        requested = self.dist_root / parsed.path.lstrip("/")
        if parsed.path == "/" or not requested.exists():
            self.path = "/index.html"
        return super().do_GET()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dist", required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5183)
    args = parser.parse_args()

    QAHandler.dist_root = Path(args.dist).resolve()
    server = ThreadingHTTPServer((args.host, args.port), lambda *handler_args: QAHandler(*handler_args, directory=str(QAHandler.dist_root)))
    print(f"Serving {QAHandler.dist_root} at http://{args.host}:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
