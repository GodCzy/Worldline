# Evidence

## Static Checks

- Command: `rg -n "Save Handoff|handoffSaveBusy|saveAgentHandoffCapsule|handoffArtifactRegistryPayload|formatAgentHandoffMarkdown|agent_handoff_capsule|savedHandoffArtifact|primarySavedReplayArtifact" web/src/views/worldline/WorldlineAgentWorkbenchView.vue`
- Result: found the new save button, save state, payload builder, markdown formatter, registry kind, saved handoff state, and replay artifact narrowing.
- Command: `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-handoff-artifact-save`
- Result: passed.

## Frontend Build

- Command: `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- Result: passed.
- Note: Vite still reports existing vendor large chunk warnings for bundles such as `vendor-antdv`, `vendor-g6`, and `vendor-mindmap`; this stage did not change code splitting.

## Browser QA

- Script: `.ai/tasks/2026-06-05-agent-handoff-artifact-save/qa-handoff-artifact-save.cjs`
- URL: `http://127.0.0.1:5173/worldline/agent`
- Result: passed.
- Assertions covered:
  - `AGENT HANDOFF` panel is visible.
  - `Save Handoff` action is visible.
  - `Save Handoff` is disabled in local non-admin preview.
  - Capsule preview includes `"write_scope": "none"`.
  - Capsule preview includes `worldline.inspect_run_artifacts`.
  - Capsule preview includes `"include_content": false`.
- Screenshot: `.ai/tasks/2026-06-05-agent-handoff-artifact-save/screenshots/handoff-artifact-save-disabled.png`

## Visual QA

- Screenshot checked: `Save Handoff` is visible and disabled, while the handoff capsule preview remains readable.
- No incoherent overlap was observed across left rail, central timeline area, and right replay rail.

## Temporary Browser Cleanup

- Started a dedicated Chrome CDP instance on port `9346` with task-local profile `chrome-profile`.
- Stopped Chrome processes whose command line referenced that profile.
- Removed the task-local `chrome-profile`; final existence check returned `False`.
