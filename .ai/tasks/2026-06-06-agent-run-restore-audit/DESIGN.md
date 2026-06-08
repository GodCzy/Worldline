# Design

## Backend

`WorldlineRunLedgerService.restore_run(run_id, payload, actor)` will:

- Load the run from the JSON ledger.
- Return `None` when the run does not exist.
- Read `maintenance.previousStatus` and restore to that value unless it is empty or `archived`.
- Fall back to `ready` when there is no usable previous status.
- Clear top-level `archivedAt` and `archivedBy` markers.
- Preserve a `maintenance.lastRestoredAt`, `maintenance.lastRestoredBy`, and `maintenance.restoredFromStatus` record.
- Append a `run.restored` event.

The route `POST /api/worldline/runs/{run_id}/restore` will remain admin-only through the existing router dependency.

## Frontend

The Run Selector row action becomes conditional:

- `Archive` for non-archived rows.
- `Restore` for archived rows.

The active run can also be restored if it is archived. `mergeLedgerResult` will keep the active workbench hydrated from the restored result.

## Validation

- Focused pytest route contract.
- Focused run ledger/live service suite.
- Vite build.
- `git diff --check`.
- Chrome CDP browser QA with mocked API responses.
