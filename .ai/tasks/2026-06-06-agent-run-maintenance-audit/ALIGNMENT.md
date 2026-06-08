# Alignment

## Goal

Add audited run maintenance actions to the Agent Workbench so operators can rename and archive saved backend runs without losing ledger history.

## Scope

- Add `WorldlineRunLedgerService.rename_run`.
- Add `WorldlineRunLedgerService.archive_run`.
- Add admin-only routes for rename and archive.
- Add focused service/route tests for audit events and list visibility.
- Add frontend selector controls for renaming the active run and archiving listed runs.
- Preserve existing load, filter, compare, manifest, and resource drilldown behavior.

## Out Of Scope

- No deletion.
- No database schema change.
- No bulk actions.
- No restore/unarchive in this increment.
- No automatic hiding of archived runs unless filtered by status.

## Acceptance

- Rename updates title, `updatedAt`, and emits `run.renamed`.
- Archive sets `status=archived`, lifecycle fields, `updatedAt`, and emits `run.archived`.
- Frontend can rename the active backend run and archive a listed backend run.
- Browser QA proves rename request, archive request, audit feedback, and archived row state.
- Pytest, Vite build, diff check, screenshot QA, and OutputMD summary are recorded.
