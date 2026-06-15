from __future__ import annotations

import copy
import hashlib
import json
import re
from typing import Any


PUBLIC_DEMO_GENERATED_AT = "2026-06-15T00:00:00Z"
PUBLIC_DEMO_SHARE_ID = "demo-branch-evidence"
PUBLIC_DEMO_PROTOCOL = "worldline-public-demo-v0.1"
EVIDENCE_BUNDLE_PROTOCOL = "worldline-evidence-bundle-v0.1"

SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)\b(password|passwd|secret)\s*[:=]\s*[^\s,;]{6,}"),
    re.compile(r"(?i)\btoken\s*[:=]\s*[A-Za-z0-9_\-\.]{12,}"),
    re.compile(r"(?i)\b(api[_-]?key)\s*[:=]\s*[A-Za-z0-9_\-\.]{12,}"),
)


PUBLIC_DEMO_DATASET: dict[str, Any] = {
    "protocolVersion": PUBLIC_DEMO_PROTOCOL,
    "datasetId": "worldline-public-demo-safety-v1",
    "title": "Worldline Public Demo Dataset",
    "generatedAt": PUBLIC_DEMO_GENERATED_AT,
    "description": (
        "A deterministic, repo-safe demo of Evidence-backed LLM Wiki and Temporal Knowledge Graph "
        "collaboration surfaces."
    ),
    "sourceMaterial": [
        {
            "id": "src-public-demo-doc",
            "label": "Public demo contract",
            "kind": "markdown",
            "sourceUri": "docs/product/public-demo.md",
            "lineStart": 1,
            "lineEnd": 80,
            "license": "project-internal-demo",
        },
        {
            "id": "src-release-gate",
            "label": "Release gate contract",
            "kind": "python",
            "sourceUri": "src/services/worldline_release_gate_service.py",
            "lineStart": 1,
            "lineEnd": 360,
            "license": "project-internal-demo",
        },
        {
            "id": "src-branch-canvas",
            "label": "Worldline branch canvas",
            "kind": "vue",
            "sourceUri": "web/src/components/worldline/WorldlineBranchCanvas.vue",
            "lineStart": 1,
            "lineEnd": 220,
            "license": "project-internal-demo",
        },
    ],
    "shareViews": [
        {
            "shareId": PUBLIC_DEMO_SHARE_ID,
            "route": f"/worldline/share/{PUBLIC_DEMO_SHARE_ID}",
            "branchId": "branch-evidence",
            "mode": "read_only",
            "allowedActions": ["inspect", "download_json_bundle", "download_markdown_bundle"],
        }
    ],
    "worldline": {
        "themeId": "public-demo",
        "rootQuestion": "How can Worldline share an evidence-backed branch safely?",
        "status": "demo_ready",
        "knowledgeMode": "llm_wiki_primary_rag_auxiliary",
        "protocolVersion": PUBLIC_DEMO_PROTOCOL,
        "activeBranchId": "branch-evidence",
        "selectedNodeId": "branch-evidence",
        "displayMeta": {
            "stageLabel": "PUBLIC DEMO",
            "stageTitle": "Read-only evidence branch",
            "stageSubtitle": "A safe branch share with evidence, graph, timeline, and replay export.",
            "themeName": "Worldline Public Demo",
        },
        "tree": {
            "width": 1100,
            "height": 620,
            "nodes": [
                {
                    "id": "root",
                    "type": "root",
                    "label": "Share safely",
                    "title": "Public demo start",
                    "x": 90,
                    "y": 310,
                },
                {
                    "id": "branch-evidence",
                    "type": "branch",
                    "branchId": "branch-evidence",
                    "label": "Evidence path",
                    "title": "Evidence-first branch",
                    "status": "ready",
                    "x": 420,
                    "y": 170,
                },
                {
                    "id": "branch-readonly",
                    "type": "branch",
                    "branchId": "branch-readonly",
                    "label": "Read-only path",
                    "title": "Share boundary",
                    "status": "ready",
                    "x": 430,
                    "y": 315,
                },
                {
                    "id": "branch-export",
                    "type": "branch",
                    "branchId": "branch-export",
                    "label": "Export path",
                    "title": "Replay capsule",
                    "status": "ready",
                    "x": 420,
                    "y": 460,
                },
                {
                    "id": "demo-ready",
                    "type": "convergence",
                    "label": "Demo ready",
                    "title": "Controlled external use",
                    "x": 930,
                    "y": 310,
                },
            ],
            "edges": [
                {
                    "id": "edge-root-evidence",
                    "source": "root",
                    "target": "branch-evidence",
                    "branchId": "branch-evidence",
                    "kind": "branch",
                    "isHighlighted": True,
                },
                {
                    "id": "edge-root-readonly",
                    "source": "root",
                    "target": "branch-readonly",
                    "branchId": "branch-readonly",
                    "kind": "branch",
                },
                {
                    "id": "edge-root-export",
                    "source": "root",
                    "target": "branch-export",
                    "branchId": "branch-export",
                    "kind": "branch",
                },
                {
                    "id": "edge-evidence-ready",
                    "source": "branch-evidence",
                    "target": "demo-ready",
                    "branchId": "branch-evidence",
                    "kind": "convergence",
                    "isHighlighted": True,
                },
                {
                    "id": "edge-readonly-ready",
                    "source": "branch-readonly",
                    "target": "demo-ready",
                    "branchId": "branch-readonly",
                    "kind": "convergence",
                },
                {
                    "id": "edge-export-ready",
                    "source": "branch-export",
                    "target": "demo-ready",
                    "branchId": "branch-export",
                    "kind": "convergence",
                },
            ],
        },
        "branches": [
            {
                "id": "branch-evidence",
                "title": "Evidence-first branch",
                "branchType": "evidence_review",
                "hypothesis": "A public share is safe only when each visible claim links to curated evidence.",
                "action": "Expose source, wiki, graph, timeline, and gate refs without live write access.",
                "result": "The branch can be inspected and exported without credentials or mutable operations.",
                "status": "approved",
                "score": 0.94,
                "evidenceIds": ["ev-public-demo-doc", "ev-release-gate", "ev-share-route"],
                "wikiRefs": ["wiki-public-demo"],
                "entityRefs": ["entity-public-demo-service", "entity-read-only-share"],
                "timelineRefs": ["tf-public-demo-freeze"],
                "gateResultIds": ["gate-no-secrets", "gate-read-only"],
                "routeTrace": {
                    "sourceIds": ["src-public-demo-doc", "src-release-gate"],
                    "evidenceIds": ["ev-public-demo-doc", "ev-release-gate", "ev-share-route"],
                    "wikiIds": ["wiki-public-demo"],
                    "entityIds": ["entity-public-demo-service", "entity-read-only-share"],
                    "timelineIds": ["tf-public-demo-freeze"],
                    "gateIds": ["gate-no-secrets", "gate-read-only"],
                    "counts": {"evidence": 3, "wiki": 1, "entities": 2, "timeline": 1, "gates": 2},
                },
            },
            {
                "id": "branch-readonly",
                "title": "Read-only share boundary",
                "branchType": "permission_boundary",
                "hypothesis": "External viewers should not inherit admin, KB, MCP, or run-ledger write rights.",
                "action": "Serve deterministic demo data from public read-only endpoints.",
                "result": (
                    "The public route has no write form, no admin dependency, and no secret-bearing request body."
                ),
                "status": "approved",
                "score": 0.91,
                "evidenceIds": ["ev-share-route"],
                "gateResultIds": ["gate-read-only"],
            },
            {
                "id": "branch-export",
                "title": "Evidence bundle capsule",
                "branchType": "export",
                "hypothesis": "A shared branch should carry a replayable capsule for review and rollback.",
                "action": "Bundle branch, evidence, graph, timeline, gates, replay steps, and checksum.",
                "result": "Reviewers can export JSON or Markdown without touching live services.",
                "status": "approved",
                "score": 0.9,
                "evidenceIds": ["ev-release-gate"],
                "gateResultIds": ["gate-bundle-checksum"],
            },
        ],
        "evidenceRefs": [
            {
                "id": "ev-public-demo-doc",
                "evidenceId": "ev-public-demo-doc",
                "title": "Public demo positioning",
                "type": "doc",
                "typeLabel": "EvidenceAnchor",
                "summary": "Worldline is demoed as evidence-backed Wiki and Temporal Knowledge Graph OS.",
                "sourceUri": "docs/product/public-demo.md",
                "lineStart": 1,
                "lineEnd": 48,
                "sourceRef": {
                    "id": "src-public-demo-doc",
                    "kind": "Markdown",
                    "label": "Public demo documentation",
                    "documentNodeId": "docnode-public-demo-positioning",
                    "documentNodeLabel": "Demo positioning",
                },
            },
            {
                "id": "ev-release-gate",
                "evidenceId": "ev-release-gate",
                "title": "Public demo release gate",
                "type": "service",
                "typeLabel": "ReleaseGate",
                "summary": (
                    "Static release gate verifies docs, governance, operational readiness, P5 share/export, "
                    "and QA evidence."
                ),
                "sourceUri": "src/services/worldline_release_gate_service.py",
                "lineStart": 1,
                "lineEnd": 420,
                "sourceRef": {
                    "id": "src-release-gate",
                    "kind": "Python service",
                    "label": "WorldlineReleaseGateService",
                    "documentNodeId": "docnode-release-gate",
                    "documentNodeLabel": "Release gate service",
                },
            },
            {
                "id": "ev-share-route",
                "evidenceId": "ev-share-route",
                "title": "Read-only share route",
                "type": "frontend",
                "typeLabel": "VueRoute",
                "summary": "The public share route renders a read-only branch and export actions without login state.",
                "sourceUri": "web/src/views/worldline/WorldlinePublicShareView.vue",
                "lineStart": 1,
                "lineEnd": 360,
                "sourceRef": {
                    "id": "src-share-view",
                    "kind": "Vue",
                    "label": "Worldline public share view",
                    "documentNodeId": "docnode-public-share-view",
                    "documentNodeLabel": "Read-only branch share",
                },
            },
        ],
        "wikiRefs": [
            {
                "id": "wiki-public-demo",
                "title": "Safe Public Demo",
                "slug": "safe-public-demo",
                "status": "approved_demo",
                "evidenceCoverage": 1.0,
                "summary": (
                    "A curated branch share demonstrates Worldline evidence flow without exposing live credentials."
                ),
                "evidenceIds": ["ev-public-demo-doc", "ev-release-gate", "ev-share-route"],
            }
        ],
        "entityRefs": [
            {
                "id": "entity-public-demo-service",
                "name": "WorldlinePublicDemoService",
                "type": "service_boundary",
                "confidence": 0.96,
                "evidenceId": "ev-release-gate",
                "summary": "Owns deterministic, safe, public demo data and bundle export.",
            },
            {
                "id": "entity-read-only-share",
                "name": "ReadOnlyShareView",
                "type": "frontend_surface",
                "confidence": 0.94,
                "evidenceId": "ev-share-route",
                "summary": "Displays a branch and export capsule without write controls.",
            },
        ],
        "relationshipRefs": [
            {
                "id": "rel-service-view",
                "source": "entity-public-demo-service",
                "target": "entity-read-only-share",
                "type": "feeds",
                "confidence": 0.93,
                "evidenceId": "ev-share-route",
            }
        ],
        "timelineRefs": [
            {
                "id": "tf-public-demo-freeze",
                "label": "Public demo dataset frozen for reproducible screenshots",
                "validFrom": "2026-06-15",
                "validTo": "present",
                "status": "observed",
                "evidenceId": "ev-public-demo-doc",
            }
        ],
        "quality": {
            "status": "demo_ready",
            "evidenceCount": 3,
            "citationCoverage": 1.0,
            "graphSupport": True,
            "temporalSupport": True,
            "publicSafety": "passed",
        },
        "gateResults": [
            {
                "id": "gate-no-secrets",
                "label": "No secrets in public demo payload",
                "status": "passed",
                "value": "0 violations",
                "threshold": "0",
                "summary": "Payload scan found no token-like or password-like values.",
            },
            {
                "id": "gate-read-only",
                "label": "Read-only public boundary",
                "status": "passed",
                "value": "0 write endpoints",
                "threshold": "0",
                "summary": "Public endpoints expose only GET routes and deterministic demo data.",
            },
            {
                "id": "gate-bundle-checksum",
                "label": "Evidence bundle checksum",
                "status": "passed",
                "value": "sha256 available",
                "threshold": "stable checksum",
                "summary": "Export capsules include a canonical JSON checksum.",
            },
        ],
    },
    "replayCapsule": {
        "id": "replay-public-demo-branch",
        "title": "Replay public evidence branch",
        "steps": [
            "Open /worldline/share/demo-branch-evidence.",
            "Inspect branch evidence, wiki, graph, timeline, and quality gate refs.",
            "Export JSON or Markdown evidence bundle.",
            "Compare checksum before sharing externally.",
        ],
        "rollback": [
            "Remove the public-demo router from server/routers/__init__.py.",
            "Remove /worldline/share/:shareId from web/src/router/index.js.",
            "Re-run release gate and frontend build.",
        ],
    },
}


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _stable_checksum(value: Any) -> str:
    return f"sha256:{hashlib.sha256(_canonical_json(value).encode('utf-8')).hexdigest()}"


class WorldlinePublicDemoService:
    """Read-only public demo dataset, branch share, and evidence bundle export service."""

    def get_dataset(self) -> dict[str, Any]:
        payload = copy.deepcopy(PUBLIC_DEMO_DATASET)
        payload["safety"] = self.safety_report(payload)
        payload["checksum"] = _stable_checksum(self._without_volatile(payload))
        return payload

    def get_branch_share(self, share_id: str = PUBLIC_DEMO_SHARE_ID) -> dict[str, Any] | None:
        share = self._find_share(share_id)
        if not share:
            return None

        dataset = self.get_dataset()
        worldline = _as_dict(dataset.get("worldline"))
        branch_id = str(share.get("branchId") or "")
        branch = self._find_branch(worldline, branch_id)
        if not branch:
            return None

        bundle = self.build_evidence_bundle(share_id=share_id)
        return {
            "protocolVersion": PUBLIC_DEMO_PROTOCOL,
            "shareId": share_id,
            "readOnly": True,
            "mode": "read_only",
            "generatedAt": PUBLIC_DEMO_GENERATED_AT,
            "dataset": self._dataset_summary(dataset),
            "share": share,
            "branch": branch,
            "worldline": {
                **worldline,
                "activeBranchId": branch_id,
                "selectedNodeId": branch_id,
                "replayCapsule": copy.deepcopy(_as_dict(dataset.get("replayCapsule"))),
            },
            "bundlePreview": {
                "bundleId": bundle["bundleId"],
                "checksum": bundle["checksum"],
                "sections": list(bundle["sections"].keys()),
                "replayStepCount": len(bundle["replayCapsule"]["steps"]),
            },
            "safety": dataset["safety"],
        }

    def build_evidence_bundle(
        self,
        *,
        share_id: str = PUBLIC_DEMO_SHARE_ID,
    ) -> dict[str, Any]:
        share = self._find_share(share_id)
        if not share:
            raise ValueError(f"Unknown public demo share id: {share_id}")

        dataset = self.get_dataset()
        worldline = _as_dict(dataset.get("worldline"))
        branch_id = str(share.get("branchId") or "")
        branch = self._find_branch(worldline, branch_id)
        if not branch:
            raise ValueError(f"Public demo branch not found: {branch_id}")

        bundle = {
            "protocolVersion": EVIDENCE_BUNDLE_PROTOCOL,
            "bundleId": f"bundle-{share_id}",
            "shareId": share_id,
            "exportedAt": PUBLIC_DEMO_GENERATED_AT,
            "readOnly": True,
            "dataset": self._dataset_summary(dataset),
            "branch": branch,
            "sections": {
                "evidence": self._select_refs(worldline, "evidenceRefs", branch.get("evidenceIds")),
                "wiki": self._select_refs(worldline, "wikiRefs", branch.get("wikiRefs")),
                "entities": self._select_refs(worldline, "entityRefs", branch.get("entityRefs")),
                "relationships": _as_list(worldline.get("relationshipRefs")),
                "timeline": self._select_refs(worldline, "timelineRefs", branch.get("timelineRefs")),
                "qualityGates": self._select_refs(worldline, "gateResults", branch.get("gateResultIds")),
            },
            "replayCapsule": copy.deepcopy(_as_dict(dataset.get("replayCapsule"))),
            "safety": dataset["safety"],
        }
        bundle["checksum"] = _stable_checksum(bundle)
        return bundle

    def build_bundle_markdown(self, *, share_id: str = PUBLIC_DEMO_SHARE_ID) -> str:
        bundle = self.build_evidence_bundle(share_id=share_id)
        branch = _as_dict(bundle.get("branch"))
        sections = _as_dict(bundle.get("sections"))
        replay = _as_dict(bundle.get("replayCapsule"))
        lines = [
            f"# {bundle['bundleId']}",
            "",
            f"- Protocol: `{bundle['protocolVersion']}`",
            f"- Share: `{bundle['shareId']}`",
            f"- Branch: `{branch.get('title') or branch.get('id')}`",
            f"- Checksum: `{bundle['checksum']}`",
            f"- Read only: `{str(bundle['readOnly']).lower()}`",
            "",
            "## Branch",
            "",
            str(branch.get("hypothesis") or ""),
            "",
            "## Evidence",
        ]
        for item in _as_list(sections.get("evidence")):
            lines.append(
                f"- `{item.get('id')}` {item.get('title')}: {item.get('sourceUri')}:{item.get('lineStart')}"
            )
        lines.extend(["", "## Quality Gates"])
        for item in _as_list(sections.get("qualityGates")):
            lines.append(f"- `{item.get('id')}` {item.get('label')}: {item.get('status')} ({item.get('value')})")
        lines.extend(["", "## Replay Capsule"])
        for index, step in enumerate(_as_list(replay.get("steps")), start=1):
            lines.append(f"{index}. {step}")
        lines.extend(["", "## Rollback"])
        for item in _as_list(replay.get("rollback")):
            lines.append(f"- {item}")
        return "\n".join(lines).strip() + "\n"

    def safety_report(self, payload: Any | None = None) -> dict[str, Any]:
        target = PUBLIC_DEMO_DATASET if payload is None else payload
        text = _canonical_json(target)
        violations = []
        for pattern in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                violations.append(
                    {
                        "pattern": pattern.pattern,
                        "start": match.start(),
                        "sample": self._redact(match.group(0)),
                    }
                )
        return {
            "status": "passed" if not violations else "failed",
            "public": True,
            "readOnly": True,
            "secretViolations": violations,
            "scannedCharacters": len(text),
            "rules": [
                "no token-like strings",
                "no password-like strings",
                "no personal credentials",
                "no public write operation",
            ],
        }

    def _find_share(self, share_id: str) -> dict[str, Any] | None:
        normalized = str(share_id or "").strip() or PUBLIC_DEMO_SHARE_ID
        for share in _as_list(PUBLIC_DEMO_DATASET.get("shareViews")):
            if str(_as_dict(share).get("shareId") or "") == normalized:
                return copy.deepcopy(_as_dict(share))
        return None

    @staticmethod
    def _find_branch(worldline: dict[str, Any], branch_id: str) -> dict[str, Any] | None:
        for branch in _as_list(worldline.get("branches")):
            normalized = _as_dict(branch)
            if str(normalized.get("id") or "") == branch_id:
                return copy.deepcopy(normalized)
        return None

    @staticmethod
    def _select_refs(
        worldline: dict[str, Any],
        key: str,
        selected_ids: Any,
    ) -> list[dict[str, Any]]:
        ids = {str(item) for item in _as_list(selected_ids)}
        refs = [_as_dict(item) for item in _as_list(worldline.get(key))]
        if not ids:
            return copy.deepcopy(refs)
        return [copy.deepcopy(item) for item in refs if str(item.get("id") or item.get("evidenceId") or "") in ids]

    @staticmethod
    def _dataset_summary(dataset: dict[str, Any]) -> dict[str, Any]:
        return {
            "datasetId": dataset.get("datasetId"),
            "title": dataset.get("title"),
            "generatedAt": dataset.get("generatedAt"),
            "sourceMaterial": copy.deepcopy(_as_list(dataset.get("sourceMaterial"))),
            "shareViews": copy.deepcopy(_as_list(dataset.get("shareViews"))),
            "checksum": dataset.get("checksum"),
        }

    @staticmethod
    def _without_volatile(payload: dict[str, Any]) -> dict[str, Any]:
        value = copy.deepcopy(payload)
        value.pop("checksum", None)
        value.pop("safety", None)
        return value

    @staticmethod
    def _redact(value: str) -> str:
        if len(value) <= 8:
            return "***"
        return f"{value[:4]}...{value[-4:]}"
