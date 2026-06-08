# Design

## Backend

`WorldlineRunLedgerService.list_runs(limit, offset)` reads the file-backed ledger and returns compact run summaries:

- `id`
- `title`
- `status`
- `createdAt`
- `updatedAt`
- `createdBy`
- `themeId`
- `rootQuestion`
- `activeBranchId`
- `qualitySummary`
- counts for branches, episodes, tools, gates, artifacts, evidence, wiki, graph, timeline, skills, events

Route:

- `GET /api/worldline/runs?limit=&offset=`
- admin-only
- read-only

## Frontend

Add `worldlineRunApi.listRuns(params)`.

In the Agent Workbench run ledger panel:

- show a compact `RUN SELECTOR` panel;
- `Refresh Runs` loads backend list;
- each listed run can be loaded via `Load`;
- loading a run calls existing `getRun` and `mergeLedgerResult`;
- manifest/resource detail snapshots are reset after switching runs.

## Validation

- Focused pytest for route list behavior.
- Full focused run ledger/MCP suite.
- Vite build.
- CDP browser QA with mocked backend list/get responses.
