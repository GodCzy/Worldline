# Alignment

Date: 2026-06-08

## Goal

Advance P3-2 Temporal Knowledge Graph by making conflicting temporal facts explicitly reviewable.

The first vertical slice is backend-focused:

- Detect temporal conflicts from evidence-bound `TemporalFact` records.
- Persist conflict review metadata onto affected facts.
- Expose conflict state through timeline serialization.
- Preserve the same conflict metadata in the read-only Neo4j projection.

## Scope

- `src/services/knowledge_graph_service.py`
- `src/repositories/knowledge_graph_repository.py`
- Focused pytest in `test/test_worldline_live_services.py`

## Non-goals

- No schema migration.
- No direct Neo4j writes.
- No `/graph` UI redesign in this slice.
- No new dependencies.

## Acceptance Evidence

- Focused pytest proves conflicting facts return `needs_review`.
- Timeline items expose `conflict_status` and conflict metadata.
- Neo4j projection temporal facts include conflict metadata.
- Existing clean graph/timeline test remains green.
