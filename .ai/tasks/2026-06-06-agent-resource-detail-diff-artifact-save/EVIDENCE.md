# Evidence

## Planned Checks

- `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-06-agent-resource-detail-diff-artifact-save`
- `& 'C:\Users\Joy\AppData\Local\OpenAI\Codex\bin\5b9024f90663758b\node.exe' '.ai\tasks\2026-06-06-agent-resource-detail-diff-artifact-save\qa-resource-detail-diff-artifact-save-cdp.mjs'`
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- in-app Browser smoke check on `http://127.0.0.1:5173/worldline/agent`

## Results

## Implementation

- Added `Save Diff Artifact` to the Resource Detail diff panel.
- Added `resource_detail_diff` artifact classification in the Registry and a `Diff` filter.
- Added structured diff artifact content with schema `worldline.resource_detail_diff.v0.1`.
- Added markdown output for human audit review.
- Preserved current Resource Detail and diff state after artifact registration and event refresh.
- Kept the change on existing frontend and run-ledger artifact contracts; no backend route or schema changes.

## Validation Results

- `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-06-agent-resource-detail-diff-artifact-save`
  - Passed.
- `& 'C:\Users\Joy\AppData\Local\OpenAI\Codex\bin\5b9024f90663758b\node.exe' '.ai\tasks\2026-06-06-agent-resource-detail-diff-artifact-save\qa-resource-detail-diff-artifact-save-cdp.mjs'`
  - Passed.
  - Verified the saved snapshot read request uses `include_content=true`.
  - Verified the diff save request posts `kind: resource_detail_diff`.
  - Verified the payload content schema is `worldline.resource_detail_diff.v0.1`.
  - Verified summary counts: `5 changed`, `6 added`, `1 removed`.
  - Verified the Registry shows `Resource Detail Diff: Current Source Detail vs Saved Source Detail` under the `Diff` class.
  - Screenshot: `D:\dev\Worldline\.ai\tasks\2026-06-06-agent-resource-detail-diff-artifact-save\screenshots\resource-detail-diff-artifact-save.png`
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
  - Passed in 5m 27s.
  - Existing Vite warning remains: `vendor-g6` and `vendor-antdv` chunks exceed 500 kB after minification.
- in-app Browser smoke on `http://127.0.0.1:5173/worldline/agent`
  - Passed.
  - Confirmed `.app-layout`, `.agent-workbench`, run selector, and Artifact Registry render.
  - Console `error`/`warn` logs: none.
  - Screenshot: `D:\dev\Worldline\.ai\tasks\2026-06-06-agent-resource-detail-diff-artifact-save\screenshots\in-app-browser-smoke.png`

## Cleanup

- Confirmed the task-local Chrome profile is removed after CDP QA.
- Confirmed CDP port `9408` has no residual listener.
