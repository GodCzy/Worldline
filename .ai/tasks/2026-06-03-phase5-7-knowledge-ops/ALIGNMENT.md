# Phase 5-7 Knowledge Ops Alignment

Updated: 2026-06-03

## Goal

Complete phases 5, 6, and 7 from `D:\document\Worldline\PROJECT_BOOK.md`.

Authoritative scope:

- Phase 5: graph and temporal layer.
- Phase 6: Worldline MCP Server and Agent workflow.
- Phase 7: evaluation and production readiness.

## Requirements

Phase 5:

- Extract entities and relationships.
- Bind extracted graph objects to evidence.
- Add `TemporalFact`, timeline, and stale page detector.

Phase 6:

- Publish Worldline MCP Server.
- Use LangGraph as the workflow orchestration shape.
- Keep ARQ as the async dispatch boundary.

Phase 7:

- Golden set.
- Coverage map.
- CI gate.
- Failure replay.
- Tracing, cost statistics, latency statistics, and permission checks.

## In Scope

- PostgreSQL contracts for local graph, temporal facts, golden set, quality gate runs, and workflow runs.
- Deterministic extraction from Phase 3 evidence-bound chunks.
- Controlled MCP server entrypoint and manifest.
- Admin-only API endpoints through the existing knowledge router.
- Deterministic quality gate with persistent results and replay payloads.
- Service tests and PostgreSQL smoke evidence.

## Out of Scope

- Full semantic NER/RE model integration.
- Neo4j write sync.
- LangGraph runtime execution with external workers.
- Real ARQ Redis enqueue in tests.
- Frontend UI.
- Secret handling, account login, paid service setup, or new high-permission MCP installation.

## Acceptance Criteria

- Graph rebuild creates evidence-bound entities and relationships.
- Timeline contains `TemporalFact` rows from source text dates.
- Stale page detector compares `WikiPage.freshness` against current source chunks.
- Worldline MCP manifest lists controlled tools and marks write tools admin-only.
- Workflow plan records LangGraph and ARQ metadata.
- Quality gate builds a golden set, coverage map, metrics, permission checks, tracing, cost stats, latency stats, and failure replay.
- Tests and smoke verification prove the above in current state.
