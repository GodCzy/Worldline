# Worldline Agent Source Dossier Alignment

Date: 2026-06-05

## Goal

Upgrade the Agent Workbench evidence chain so an EvidenceAnchor can focus the exact SourceAsset / DocumentNode location that supports a branch, gate, graph node, or temporal fact.

## Current Gap

- Evidence refs already carry `sourceUri`, `lineStart`, and `lineEnd`.
- The UI currently shows those fields as static text only.
- Focusable Dossier types cover Evidence, Wiki, Graph, Timeline, Tool, Gate, Artifact, Permission, and Skill, but not Source.
- Gate coverage can show supporting Evidence / Graph / Time counts, but the last hop to file-level source context is missing.

## Scope

- Add local SourceAsset / DocumentNode metadata to the Agent Workbench fallback data.
- Add a focusable Source Dossier type derived from EvidenceAnchor source metadata.
- Link Evidence Dossiers to Source Dossiers.
- Link Gate Dossiers to source locations through their supporting evidence.
- Preserve the existing frontend store contract and backend API contract.

## Out Of Scope

- No backend schema or router change.
- No new dependency.
- No automatic editor/file opener integration.
- No mutation of unrelated dirty worktree files.

## Acceptance

- Evidence Dossier exposes a clickable Source link.
- Source Dossier shows source uri, line range, source kind, document node, and backlink to Evidence.
- Gate Dossier can surface source links for its supporting evidence.
- Frontend build passes.
- Screenshot evidence captures Source focus and backlink behavior.
