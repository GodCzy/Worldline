# Decisions

## Archive is not delete

Archive changes run state to `archived` and adds lifecycle metadata. It does not remove run, events, artifacts, evidence, or knowledge refs.

## Audit event first

Every maintenance mutation emits a ledger event. The UI relies on the returned `latestEvent` to keep the event lane auditable.

## Active-run rename only

This increment supports renaming the active backend run from the selector panel. Bulk or per-row rename can be added later.
