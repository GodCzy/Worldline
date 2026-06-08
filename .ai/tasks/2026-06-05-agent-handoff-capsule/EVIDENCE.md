# Evidence

## Static Checks

- Command: `rg -n "AGENT HANDOFF|agentHandoffCapsule|copyHandoffCapsule|handoff-capsule|worldline-agent-handoff" web/src/views/worldline/WorldlineAgentWorkbenchView.vue`
- Result: found the new template, state, copy action, protocol, and styles.
- Command: `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-handoff-capsule`
- Result: passed.

## Frontend Build

- Command: `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- Result: passed.
- Note: Vite still reports existing vendor large chunk warnings for bundles such as `vendor-antdv`, `vendor-g6`, and `vendor-mindmap`; this stage did not change code splitting.

## Browser QA

- Script: `.ai/tasks/2026-06-05-agent-handoff-capsule/qa-agent-handoff-capsule.cjs`
- URL: `http://127.0.0.1:5173/worldline/agent`
- Result: passed.
- Assertions covered:
  - `AGENT HANDOFF` panel is visible inside Replay Export.
  - Protocol is `worldline-agent-handoff@0.1`.
  - Capsule preview includes `"write_scope": "none"`.
  - Capsule preview includes `worldline.inspect_run_artifacts`.
  - Capsule preview includes `"include_content": false`.
  - Capsule preview includes `worldline-run-ledger://run-agent-workbench-preview/artifacts/replay-export-preview-run-created`.
  - `Copy Handoff` produces copied or clipboard fallback status.
- Screenshots:
  - `.ai/tasks/2026-06-05-agent-handoff-capsule/screenshots/agent-handoff-capsule-preview.png`
  - `.ai/tasks/2026-06-05-agent-handoff-capsule/screenshots/agent-handoff-capsule-copy.png`

## Visual QA

- Preview screenshot checked: `AGENT HANDOFF` is compactly embedded under `MCP READABLE`; protocol, target, rollback rule, and JSON capsule are visible.
- Copy status screenshot checked: clipboard fallback status is visible and the preview remains available.
- No incoherent overlap was observed across left rail, central worldline/timeline area, and right replay rail.

## Temporary Browser Cleanup

- Started a dedicated Chrome CDP instance on port `9345` with task-local profile `chrome-profile`.
- Stopped Chrome processes whose command line referenced that profile.
- Removed the task-local `chrome-profile`; final existence check returned `False`.
- After interruption, rechecked there were no task Chrome processes and the profile remained absent.
