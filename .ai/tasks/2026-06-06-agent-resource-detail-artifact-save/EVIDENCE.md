# Evidence

## Planned Checks

- `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-06-agent-resource-detail-artifact-save`
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- Browser QA on `http://127.0.0.1:5173/worldline/agent`

## Results

## Implementation

- Added Resource Detail "Save Detail Artifact" action in `web/src/views/worldline/WorldlineAgentWorkbenchView.vue`.
- Added `worldline.resource_detail_snapshot.v0.1` payload generation with JSON content and Markdown preview.
- Reused `worldlineRunApi.registerRunArtifact` / `POST /api/worldline/runs/{run_id}/artifacts`; no backend or schema changes.
- Added saved-artifact merge handling so mutation POST responses remain visible even when the artifact list endpoint is stale or temporarily returns an empty list.
- Preserved the inspected Resource Detail after save instead of clearing the panel during ledger result merge.

## Validation

- `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-06-agent-resource-detail-artifact-save`
  - Result: pass.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
  - First run timed out after 124 seconds without a build error.
  - Re-run with a longer timeout passed in 4m 53s before the state-merge fix.
  - Final run after the state-merge fix passed in 4m 40s.
  - Remaining warning: Vite reports existing chunks above 500 kB (`vendor-g6`, `vendor-antdv`, etc.).
- `node .ai/tasks/2026-06-06-agent-resource-detail-artifact-save/qa-resource-detail-artifact-save-cdp.mjs`
  - First run failed while waiting for the saved registry message.
  - Diagnosis: event refresh called `refreshRunArtifacts()`, and an empty artifact-list response overwrote the saved artifact from the POST response.
  - Final run passed.
  - Confirmed POST to `/api/worldline/runs/run-resource-detail-save/artifacts`.
  - Confirmed payload kind `resource_detail_snapshot`.
  - Confirmed inspected response content was preserved.
  - Confirmed events refreshed to `3/3 loaded`.
  - Confirmed Registry shows `Resource Detail: Detail Save Artifact` as `Artifact / saved`.
- in-app Browser check on `http://127.0.0.1:5173/worldline/agent`
  - Result: page title `世界线 - Worldline`.
  - Confirmed `.agent-workbench` and `[data-artifact-registry="true"]` render in local-preview mode.

## Artifacts

- Chrome CDP QA screenshot: `D:\dev\Worldline\.ai\tasks\2026-06-06-agent-resource-detail-artifact-save\screenshots\resource-detail-artifact-save.png`
- Temporary QA Chrome profile was removed after path verification:
  - `D:\dev\Worldline\.ai\tasks\2026-06-06-agent-resource-detail-artifact-save\chrome-profile-cdp`
