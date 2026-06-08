# Alignment

## Goal

Add a real backend run selector to the Agent Workbench so operators can list saved Worldline runs, switch the workbench to an existing run, and continue inspecting manifest/resources from that backend run.

## Scope

- Add `WorldlineRunLedgerService.list_runs`.
- Add `GET /api/worldline/runs` route.
- Add focused route tests for run listing and ordering.
- Add frontend API helper.
- Add Agent Workbench run selector UI with refresh and load actions.
- Preserve existing save/sync/local preview behavior.

## Out Of Scope

- No database schema changes.
- No run deletion or mutation from the selector.
- No cross-run search.
- No replacement of current run ledger save/approve/reject/artifact flows.

## Acceptance

- Backend returns a paginated run list with compact run summaries.
- Frontend can load the run list from the backend ledger.
- Frontend can select a listed run and hydrate the workbench from backend data.
- Browser QA proves list request, selection, and loaded run state.
- Pytest, Vite build, diff check, screenshot QA, and OutputMD summary are recorded.
