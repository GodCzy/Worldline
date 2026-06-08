# Decisions

## 2026-06-06

- Persist the diff as a normal run artifact instead of adding a specialized backend endpoint.
- Use `resource_detail_diff` as the artifact kind so the Registry can distinguish diff reports from snapshots.
- Keep the current diff visible after saving because saving is an audit action, not a navigation action.
