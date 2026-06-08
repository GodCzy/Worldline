# Decisions

## Selector is read-only

The run selector lists and loads saved runs but does not delete, rewrite, or approve anything.

## Compact summaries first

The list endpoint returns compact summaries instead of full run payloads. Loading a specific run still uses `GET /api/worldline/runs/{run_id}`.

## Preserve local preview

The workbench remains usable without admin/backend access. Selector actions are disabled unless admin run ledger access is available.
