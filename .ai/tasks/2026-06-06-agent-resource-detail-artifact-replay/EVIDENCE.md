# Evidence

## Planned Checks

- `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-06-agent-resource-detail-artifact-replay`
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- Chrome CDP QA on `http://127.0.0.1:5173/worldline/agent`
- in-app Browser smoke check on `http://127.0.0.1:5173/worldline/agent`

## Results

## Implementation

- Added Resource Detail snapshot detection for Registry artifacts using `resource_detail_snapshot` kind or `resource-detail-*` id prefix.
- Added `Read Detail` action for saved Resource Detail snapshots.
- Added replay/read handler that calls `worldlineRunApi.inspectRunArtifact` with `include_content=true`.
- Restored saved snapshot content into the Resource Detail panel:
  - resource metadata
  - original inspect response
  - source URI and tool
  - replay-loaded status message
- Added a `Registry Replay` last-MCP-call surface so the exact read contract is visible.

## Validation

- `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-06-agent-resource-detail-artifact-replay`
  - Result: pass.
- `node .ai/tasks/2026-06-06-agent-resource-detail-artifact-replay/qa-resource-detail-artifact-replay-cdp.mjs`
  - First run failed because localStorage-only auth did not update the Pinia user store.
  - Fixed QA setup by injecting the `user` Pinia store before clicking `Refresh Runs`.
  - Final run passed.
  - Confirmed `GET /api/worldline/runs/run-resource-detail-replay/artifacts/read?artifact_id=resource-detail-run-resource-detail-replay-source-001&include_content=true&limit=20`.
  - Confirmed Resource Detail panel restored `Replay restored inspect content from saved snapshot.`
  - Confirmed Registry still shows `Resource Detail: Saved Source Detail`.
  - Confirmed Last MCP Call shows `Registry Replay` and `include_content: true`.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
  - Result: pass in 5m 9s.
  - Remaining warning: existing Vite chunks above 500 kB (`vendor-g6`, `vendor-antdv`, etc.).
- in-app Browser smoke check on `http://127.0.0.1:5173/worldline/agent`
  - First immediate read saw the title but empty body text.
  - After waiting for app mount, `.app-layout`, Worldline Agent body text, and Registry content rendered.
  - Browser error/warn logs were empty.

## Artifacts

- Chrome CDP QA screenshot: `D:\dev\Worldline\.ai\tasks\2026-06-06-agent-resource-detail-artifact-replay\screenshots\resource-detail-artifact-replay.png`
- Temporary QA Chrome profile was removed after path verification:
  - `D:\dev\Worldline\.ai\tasks\2026-06-06-agent-resource-detail-artifact-replay\chrome-profile-cdp`
