# Decisions

## 2026-06-06

- Use the existing run artifact registration endpoint; no backend changes.
- Store inspect result as `resource_detail_snapshot` JSON so it can later be replayed or diffed.
- Refresh loaded run events after save to expose backend audit events.
- Treat the artifact registration response as authoritative immediately after mutation. Event refresh may call the artifact list endpoint before storage is fully consistent, so the frontend re-merges the registered artifact after refresh.
- Preserve the loaded Resource Detail after save so the user can still inspect the exact payload that became replayable.
