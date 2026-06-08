# Evidence

## Static Checks

- Command: `rg -n "Copy MCP|copyRegistryArtifactMcpCall|registryArtifactMcpArgs|registryArtifactUri|registryArtifactRunId|registry-artifact-row|registry-mcp-button" web/src/views/worldline/WorldlineAgentWorkbenchView.vue`
- Result: found item-level shortcut template, URI/args helpers, copy handler, row style, and button style.
- Command: `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-registry-mcp-shortcut`
- Result: passed.

## Frontend Build

- Command: `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- Result: passed.
- Note: Vite still reports existing vendor large chunk warnings for bundles such as `vendor-antdv`, `vendor-g6`, and `vendor-mindmap`; this stage did not change code splitting.

## Browser QA

- Script: `.ai/tasks/2026-06-05-agent-registry-mcp-shortcut/qa-registry-mcp-shortcut.cjs`
- URL: `http://127.0.0.1:5173/worldline/agent`
- Result: passed.
- Assertions covered:
  - Planned replay and handoff artifacts are visible in Registry.
  - `Copy MCP` action is visible on Registry rows.
  - Handoff-filtered row can trigger item-level copy status.
  - Replay-filtered row can trigger item-level copy status.
- Screenshots:
  - `.ai/tasks/2026-06-05-agent-registry-mcp-shortcut/screenshots/registry-handoff-copy-mcp.png`
  - `.ai/tasks/2026-06-05-agent-registry-mcp-shortcut/screenshots/registry-replay-copy-mcp.png`

## Visual QA

- Handoff screenshot checked: `Copy MCP` is visible under `Agent Handoff: Run Preview`; fallback status identifies the handoff artifact.
- Replay screenshot checked: `Copy MCP` is visible under `Replay Export: Agent Workbench Stage 1`; fallback status identifies the replay artifact.
- No incoherent overlap was observed across left rail, central worldline/timeline area, and right replay rail.

## Temporary Browser Cleanup

- Started a dedicated Chrome CDP instance on port `9348` with task-local profile `chrome-profile`.
- Stopped Chrome processes whose command line referenced that profile.
- Removed the task-local `chrome-profile`; final existence check returned `False`.
