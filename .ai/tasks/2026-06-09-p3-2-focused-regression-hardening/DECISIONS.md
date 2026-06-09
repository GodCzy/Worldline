# Decisions

## D1. Use a pure frontend utility instead of a new test framework

Reason: the web project already has a Node assertion test style under `web/src/utils/__tests__`. Reusing it adds regression coverage without new dependencies.

## D2. Keep canvas focus best-effort

Reason: `/api/knowledge/.../graph/*` review payloads and the legacy `/api/graph/subgraph` canvas can expose different node identifiers. The route focus card remains the primary traceability surface; canvas focus is an enhancement when a matching node exists.
