# Design

## Data Shape

`WorldlinePublicDemoService` owns a deterministic, repo-safe demo payload:

`dataset -> read-only share view -> evidence bundle -> replay capsule`

The payload mirrors Worldline workbench concepts without requiring a live database:

- branches
- evidence refs
- wiki refs
- entity and relationship refs
- timeline refs
- quality gates
- replay steps

## API

- `GET /api/worldline/public-demo/dataset`
- `GET /api/worldline/public-demo/branches/{share_id}`
- `GET /api/worldline/public-demo/evidence-bundle?share_id=...&format=json|markdown`

All endpoints are read-only and public. They do not accept writes, tokens, external URLs with credentials, or secret-bearing payloads.

## Frontend

`/worldline/share/:shareId` renders a compact read-only branch share page:

- Worldline branch canvas
- selected branch summary
- evidence, wiki, graph, timeline, quality, replay panels
- JSON and Markdown evidence bundle export actions

## Release Gate

The static release gate checks:

- service and router fragments
- public path declaration
- frontend API and route fragments
- public-demo docs and rollback instructions
- P5 screenshot QA report
- secret-like marker scan over the P5 public-demo surface
