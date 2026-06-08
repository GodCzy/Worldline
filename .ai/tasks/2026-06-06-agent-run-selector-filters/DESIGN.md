# Design

## Backend

Extend `WorldlineRunLedgerService.list_runs` with optional keyword arguments:

- `query`
- `status`
- `theme_id`
- `created_by`

Filtering remains in-memory over the existing file-backed ledger. The method still returns compact summaries and keeps the current response shape, adding only a compatible `filters` object.

Route:

- `GET /api/worldline/runs?limit=&offset=&query=&status=&theme_id=&created_by=`
- admin-only
- read-only

## Frontend

The run selector gains compact controls:

- keyword input
- status select
- theme input
- created-by input
- clear filters

`Refresh Runs` passes the controls to `worldlineRunApi.listRuns`. Existing run loading continues to use `GET /api/worldline/runs/{run_id}`.

## Validation

- Focused route test for list filters.
- Full focused run ledger/MCP suite.
- Vite build.
- CDP browser QA with mocked filtered backend responses.
