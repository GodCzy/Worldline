# Alignment

## Goal

Connect Agent Replay Export to the backend run ledger so replay artifacts can be registered, listed, and replayed by other Worldline surfaces later.

## Scope

- Add compatible file-backed artifact registry methods to `WorldlineRunLedgerService`.
- Expose admin-protected `/api/worldline/runs/{run_id}/artifacts` endpoints.
- Add frontend API helpers and an Agent Workbench save/list affordance.
- Preserve local preview behavior when backend/admin access is unavailable.

## Out Of Scope

- No Postgres schema or migration.
- No MinIO binary artifact storage.
- No MCP external write endpoint in this stage.
- No destructive cleanup of unrelated dirty files.

## Acceptance

- Existing run ledger tests still pass.
- New service/router tests prove artifact registration and listing.
- Frontend build passes.
- Browser QA proves the replay export panel exposes backend artifact affordance without breaking local preview.
