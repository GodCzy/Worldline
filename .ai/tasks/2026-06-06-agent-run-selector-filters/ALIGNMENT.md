# Alignment

## Goal

Upgrade the Agent Workbench run selector from a recent-run list into a searchable backend run entry point. Operators should be able to filter saved Worldline runs before loading one into the workbench.

## Scope

- Extend `WorldlineRunLedgerService.list_runs` with compatible optional filters.
- Extend `GET /api/worldline/runs` query params.
- Add focused tests for search, status, theme, creator, ordering, and pagination.
- Add frontend API param usage and compact selector filter controls.
- Preserve current selector refresh/load behavior and local preview fallback.

## Out Of Scope

- No run deletion, archiving, renaming, or mutation.
- No database schema changes.
- No full-text index or cross-run graph search.
- No replacement of existing manifest/resource drilldown.

## Acceptance

- Backend filters runs by query text, status, theme, and creator.
- Backend response includes active filter metadata.
- Frontend selector can submit filters and load the filtered run.
- Browser QA proves filtered list request, selected run load, and artifact refresh request.
- Pytest, Vite build, diff check, screenshot QA, and OutputMD summary are recorded.
