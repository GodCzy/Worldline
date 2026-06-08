# Design

## Frontend

Add `selectedLedgerRunIds` state in `WorldlineAgentWorkbenchView.vue`.

Derived state:

- `selectedLedgerRuns`: visible/listed selected run summaries.
- `selectedLedgerRunCount`: total selected rows.
- `selectedArchiveRuns`: selected rows whose status is not `archived`.
- `selectedRestoreRuns`: selected rows whose status is `archived`.

UI:

- Add a checkbox per selector row.
- Add a compact bulk action bar under the rename form.
- Disable bulk actions when no compatible selection exists, while ledger or maintenance operations are busy, or when admin access is unavailable.

Operations:

- `archiveSelectedLedgerRuns()` calls existing `archiveLedgerRun(runId, { refresh: false })` for each compatible selected row, then refreshes once and clears selection.
- `restoreSelectedLedgerRuns()` calls existing `restoreLedgerRun(runId, { refresh: false })` for each compatible selected row, then refreshes once and clears selection.

## Backend

No new backend endpoint. This intentionally reuses audited single-run routes so each mutation still creates an individual ledger event.

## Validation

- `git diff --check`.
- `npm --prefix web run build`.
- Chrome CDP QA with mocked run list, archive, and restore responses.
