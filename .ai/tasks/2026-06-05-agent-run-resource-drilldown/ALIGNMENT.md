# Alignment

## Goal

Turn backend manifest resources into inspectable Agent Workbench resources by adding run-scoped read-only HTTP drilldown routes and frontend inspect actions for artifacts, gates, evidence/source, wiki, graph, and timeline resources.

## Scope

- Add HTTP read routes that delegate to existing run inspection service methods.
- Add frontend API helpers for run artifacts, gates, evidence/source, and knowledge.
- Extend Backend Manifest inspector resources with an `Inspect` action.
- Display selected resource details in the Agent Workbench.
- Keep all routes admin-gated and read-only.

## Out Of Scope

- No database schema changes.
- No new write MCP or write HTTP route.
- No replacement of existing MCP read tools.
- No live cross-run search.

## Acceptance

- `GET /api/worldline/runs/{run_id}/artifacts/read`
- `GET /api/worldline/runs/{run_id}/gates`
- `GET /api/worldline/runs/{run_id}/evidence`
- `GET /api/worldline/runs/{run_id}/knowledge`
- Tests prove route behavior for selected resources and missing resources.
- Frontend can click a backend manifest resource and display route-derived detail.
- Browser QA proves at least one manifest resource drilldown request and detail render.
