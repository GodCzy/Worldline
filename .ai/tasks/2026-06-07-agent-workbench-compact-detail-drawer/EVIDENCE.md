# Evidence

## Planned Checks

- `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-07-agent-workbench-compact-detail-drawer .ai/tasks/2026-06-06-agent-resource-detail-diff-artifact-save`
- `& 'C:\Users\Joy\AppData\Local\OpenAI\Codex\bin\5b9024f90663758b\node.exe' '.ai\tasks\2026-06-06-agent-resource-detail-diff-artifact-save\qa-resource-detail-diff-artifact-save-cdp.mjs'`
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- in-app Browser smoke check on `http://127.0.0.1:5173/worldline/agent`

## Results

- `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-07-agent-workbench-compact-detail-drawer .ai/tasks/2026-06-06-agent-resource-detail-diff-artifact-save`
  - Result: passed.
- Static text checks:
  - Confirmed no inline raw-preview `<pre>` remains for Resource Detail response, last MCP args, MCP readable args, or run manifest args.
  - Confirmed stale `mcpRunManifestUri` variable name is absent.
- Frontend build:
  - Command: `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && /home/joy/.local/bin/npm --prefix web run build"`
  - Result: passed in 3m48s.
  - Residual warning: Vite reports large chunks for existing vendor bundles such as `vendor-g6` and `vendor-antdv`.
- Dev server:
  - Added `start-vite-dev.sh` to avoid WSL PATH loss when npm invokes `env node`.
  - Server verified at `http://127.0.0.1:5173/worldline/agent` with HTTP 200.
  - Logs: `vite-dev-stdout.log`, `vite-dev-stderr.log`.
- CDP QA:
  - Command: `C:\Users\Joy\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe .ai\tasks\2026-06-06-agent-resource-detail-diff-artifact-save\qa-resource-detail-diff-artifact-save-cdp.mjs`
  - Result: passed.
  - Covered:
    - compact Resource Detail main panel;
    - `查看后端响应` modal exposes full backend response;
    - `最近 MCP 调用` modal exposes full MCP args;
    - resource detail diff counts and Chinese labels;
    - `resource_detail_diff` artifact POST payload and registry refresh.
  - Screenshot: `screenshots/resource-detail-diff-artifact-save.png`.
- In-app Browser smoke:
  - URL: `http://127.0.0.1:5173/worldline/agent`
  - Result: page title `世界线 - Worldline`, Chinese `Agent 工作台` and `任务选择` rendered, console error log count was 0.
  - Screenshot: `screenshots/in-app-browser-smoke.png`.
