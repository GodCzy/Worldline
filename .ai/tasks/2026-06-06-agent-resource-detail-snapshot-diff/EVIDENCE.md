# Evidence

## Planned Checks

- `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-06-agent-resource-detail-snapshot-diff`
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- Chrome CDP QA on `http://127.0.0.1:5173/worldline/agent`
- in-app Browser smoke check on `http://127.0.0.1:5173/worldline/agent`

## Results

## Implementation

- Added `Diff Detail` for saved `resource_detail_snapshot` Registry rows.
- Reused `GET /api/worldline/runs/{run_id}/artifacts/read?include_content=true` through the existing frontend API wrapper.
- Added current-vs-saved Resource Detail normalization, JSON path flattening, added/removed/changed counts, and compact changed-path preview.
- Added a Resource Detail diff panel with narrow-column responsive styling and hover titles for truncated path rows.
- Kept the change frontend-only; no backend route, schema, or write contract changed.

## Validation Results

- `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-06-agent-resource-detail-snapshot-diff`
  - Passed.
- `& 'C:\Users\Joy\AppData\Local\OpenAI\Codex\bin\5b9024f90663758b\node.exe' '.ai\tasks\2026-06-06-agent-resource-detail-snapshot-diff\qa-resource-detail-snapshot-diff-cdp.mjs'`
  - Passed.
  - Verified saved snapshot artifact read request includes `artifact_id=resource-detail-run-resource-detail-diff-source-001` and `include_content=true`.
  - Verified UI shows `ADDED`, `REMOVED`, `CHANGED`, changed paths, and Last MCP Call source `Registry Diff`.
  - Screenshot: `D:\dev\Worldline\.ai\tasks\2026-06-06-agent-resource-detail-snapshot-diff\screenshots\resource-detail-snapshot-diff.png`
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
  - Passed in 6m 10s.
  - Existing Vite warning remains: `vendor-g6` and `vendor-antdv` chunks exceed 500 kB after minification.
- in-app Browser smoke on `http://127.0.0.1:5173/worldline/agent`
  - Passed.
  - Confirmed `.app-layout`, `.agent-workbench`, run selector, and Artifact Registry render.
  - Console `error`/`warn` logs: none.
  - Screenshot: `D:\dev\Worldline\.ai\tasks\2026-06-06-agent-resource-detail-snapshot-diff\screenshots\in-app-browser-smoke-final.png`

## Failure Notes

- First rerun of the CDP script failed before page assertions because no Chrome CDP browser was already listening on port `9406`.
- Fixed the QA script to launch Chrome with a task-local temporary profile, then clean that profile after the run.
- Confirmed `D:\dev\Worldline\.ai\tasks\2026-06-06-agent-resource-detail-snapshot-diff\chrome-profile-cdp` is removed after QA.
