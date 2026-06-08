# Decisions

## 2026-06-06 Restore Is Soft Recovery

Archived runs are restored by changing status and recording an event. The implementation does not delete archive audit fields from history, does not purge events, and does not rewrite previous ledger entries beyond current run metadata.

## 2026-06-06 Default Restore Status

If `maintenance.previousStatus` is unavailable or unusable, restore falls back to `ready`. This keeps legacy archived runs recoverable without adding schema requirements.
