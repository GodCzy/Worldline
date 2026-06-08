# Design

## Backend

Routes:

- `POST /api/worldline/runs/{run_id}/rename`
- `POST /api/worldline/runs/{run_id}/archive`

Both routes are admin-only and use `WorldlineRunLedgerService`.

`rename_run` stores:

- new `title`
- `updatedAt`
- audit event `run.renamed`
- event summary with old/new title and reason

`archive_run` stores:

- `status = archived`
- `archivedAt`
- `archivedBy`
- `updatedAt`
- audit event `run.archived`
- event summary with previous status and reason

## Frontend

Inside run selector:

- add a compact rename input for the active backend run;
- add `Rename` action;
- add `Archive` action beside listed runs;
- after rename/archive, refresh run list and merge active run result when the affected run is active.

## Validation

- Focused route test for rename/archive.
- Full focused run ledger/MCP suite.
- Vite build.
- Chrome CDP QA with mocked rename/archive responses.
