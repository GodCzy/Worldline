# Alignment

Date: 2026-06-03

## Goal

Complete Phase 6 and Phase 7 for Worldline:

- Phase 6: Skill, MCP, and subagent governance.
- Phase 7: Evaluation gate, public-demo readiness, release evidence, and screenshots.

## Product Boundary

Worldline remains an Evidence-backed LLM Wiki + Temporal Knowledge Graph OS.

RAG remains an auxiliary retrieval layer. The release surface must emphasize evidence anchors, LLM Wiki, temporal graph, controlled MCP workflow, audit logs, and quality gates.

## In Scope

- Application MCP default policy.
- Controlled Worldline manifest and subagent lanes.
- Static Phase 6/7 release gate.
- Public demo document.
- Focused backend tests.
- Frontend build, docs build, docker compose config.
- Screenshot QA reuse/rerun for `/worldline`, `/worldline/phase5-preview`, and `/graph`.

## Out Of Scope

- No external MCP installation.
- No database direct-write MCP.
- No cloud write tools.
- No secret or token storage.
- No frontend redesign beyond validation.
- No Git history rewrite.

## Acceptance Criteria

- `worldline` is the only application MCP enabled by default.
- Conditional MCP configs exist but default disabled.
- Local Worldline Codex skills are discoverable.
- Subagent lanes are present in the controlled manifest.
- Release gate report returns `status=passed`.
- Tests, build, docs, docker config, and screenshots are recorded in evidence.
