# Alignment

## Goal

Add a read-only cross-run diff timeline to the Agent Workbench so operators can compare the currently loaded run with another saved backend run before switching context.

## Scope

- Add `WorldlineRunLedgerService.compare_runs`.
- Add `GET /api/worldline/runs/compare?left_run_id=&right_run_id=`.
- Compare compact resources across branches, episodes, tool traces, gates, artifacts, evidence, wiki, graph entities, timeline facts, skills, and events.
- Add focused route/service tests.
- Add frontend API helper and selector Compare action.
- Render a compact diff timeline inside the existing run selector panel.

## Out Of Scope

- No run mutation, archive, deletion, rename, or approval.
- No schema changes.
- No deep semantic diff of document contents.
- No cross-run graph visualization dependency.

## Acceptance

- Backend returns left/right run summaries and resource diff buckets.
- Frontend can compare the active ledger run with another listed run.
- Browser QA proves compare request, diff rendering, and no run switch.
- Pytest, Vite build, diff check, screenshot QA, and OutputMD summary are recorded.
