# Alignment

## Goal

Close the Agent Workbench run maintenance loop by letting operators restore a previously archived backend run without deleting ledger history.

## Scope

- Add a backend restore action for durable Worldline runs.
- Record restore as an audit event on the same run ledger.
- Expose a protected FastAPI route for restore.
- Add Agent Workbench UI affordance for archived rows.
- Validate service, route, build, diff, and browser behavior.

## Out Of Scope

- Hard delete, purge, or compact ledger history.
- Database schema migrations.
- Batch archive/restore.
- Changing MCP read contracts.
- Cleaning unrelated dirty worktree files.

## Acceptance

- Archived runs can be restored through the backend service and API.
- Restore returns the run with a non-archived status and `latestEvent.eventType == "run.restored"`.
- The restore event records previous archived status, restored status, actor, and reason.
- The Agent Workbench shows `Restore` for archived runs and `Archive` for active/non-archived runs.
- Browser QA proves the UI calls the restore endpoint and updates row state.
