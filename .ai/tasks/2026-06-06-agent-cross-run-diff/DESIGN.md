# Design

## Backend

`WorldlineRunLedgerService.compare_runs(left_run_id, right_run_id)` reads the file-backed ledger and compares resource IDs by category.

Response shape:

- `status`
- `contractVersion`
- `left`
- `right`
- `summary`
- `sections`
- `timeline`
- `storage`

Each section reports `added`, `removed`, `shared`, and counts. Added means present in right but not left. Removed means present in left but not right.

Route:

- `GET /api/worldline/runs/compare?left_run_id=&right_run_id=`
- admin-only
- read-only

## Frontend

Add `worldlineRunApi.compareRuns(params)`.

Inside the run selector list:

- keep existing Load behavior;
- add Compare for listed runs when an active backend run exists;
- render compact `RUN DIFF` panel with left/right labels, changed totals, and per-section timeline rows.

## Validation

- Focused pytest for compare route and not-found behavior.
- Full focused run ledger/MCP suite.
- Vite build.
- Chrome CDP QA with mocked compare response.
