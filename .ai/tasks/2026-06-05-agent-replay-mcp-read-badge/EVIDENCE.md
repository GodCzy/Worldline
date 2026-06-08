# Evidence

## Static Check

- Command: `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-replay-mcp-read-badge`
- Result: passed.

## Frontend Build

- Command: `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- Result: passed.
- Note: Vite still reports existing large chunk warnings for vendor bundles such as `vendor-antdv`, `vendor-g6`, and `vendor-mindmap`; this stage does not change code splitting.

## Browser QA

- Script: `.ai/tasks/2026-06-05-agent-replay-mcp-read-badge/qa-mcp-read-badge.cjs`
- URL: `http://127.0.0.1:5173/worldline/agent`
- Result: passed after making the readable-state assertion case-insensitive.
- First run failure recorded: browser `innerText` rendered `Save required` as `SAVE REQUIRED` because of style transformation, while the UI state and text were correct.
- Assertions covered:
  - `MCP READABLE` panel is visible.
  - Tool name is `worldline.inspect_run_artifacts`.
  - URI is `worldline-run-ledger://run-agent-workbench-preview/artifacts/replay-export-preview-run-created`.
  - Safe args include `"include_content": false`.
  - `Copy MCP Call` produces visible copied/clipboard fallback status.
- Screenshot: `.ai/tasks/2026-06-05-agent-replay-mcp-read-badge/screenshots/mcp-readable-badge.png`

## Temporary Browser Cleanup

- Started a dedicated Chrome CDP instance on port `9344` with task-local profile `chrome-profile`.
- Stopped Chrome processes whose command line referenced that profile.
- Removed the task-local `chrome-profile`; final existence check returned `False`.

## Final File Checks

- Confirmed screenshot, evidence file, and OutputMD summary exist.
- A combined `git diff --check` attempt failed because `D:\document\OutputMD\2026-06-05-Worldline-Agent-Replay-MCP-Read-Badge.md` is outside the `D:\dev\Worldline` repository.
- Reran repository-scoped command: `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-replay-mcp-read-badge`
- Result: passed.
