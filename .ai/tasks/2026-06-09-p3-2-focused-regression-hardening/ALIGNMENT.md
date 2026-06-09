# Alignment

Date: 2026-06-09

## Goal

Continue P3-2 Temporal Knowledge Graph by hardening graph focus regression coverage instead of adding another isolated UI entry point.

## Acceptance Target

- Graph focus query behavior is reusable and testable outside large Vue SFCs.
- Entity, relationship, conflict, timeline, evidence, Neo4j projection, and canvas focus expectations are represented in focused regression evidence.
- `/graph` and `/worldline/:themeId` behavior remains compact and traceable.
- Browser QA covers `/worldline/:themeId` and `/graph` at desktop and `390px` when the local server is available.

## In Scope

- Extract pure graph focus helpers from the current frontend implementation.
- Reuse the helpers from `/graph`, Wiki citation links, and `/worldline/:themeId`.
- Add deterministic Node assertion coverage for route focus matching and canvas node lookup.
- Run focused backend contract checks that cover graph/timeline/projection behavior.

## Out Of Scope

- No external Neo4j writes.
- No new frontend test framework dependency.
- No large copy cleanup or unrelated visual redesign.
- No connector installation without Joy selecting it.
