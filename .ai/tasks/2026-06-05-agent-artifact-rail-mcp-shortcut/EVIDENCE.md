# Evidence

## Static Checks

- Command: `rg -n "artifactRailMessage|copyArtifactRailMcpCall|registryArtifactMcpInstruction|artifact-mcp-message|artifact-mcp-button" web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-artifact-rail-mcp-shortcut`
- Result: found local Artifact Rail message state, shared MCP instruction helper, rail copy handler, message style, and button style.
- Command: `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-artifact-rail-mcp-shortcut`
- Result: passed.

## Frontend Build

- Command: `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- Result: passed.
- Note: Vite still reports existing vendor large chunk warnings for bundles such as `vendor-antdv`, `vendor-g6`, and `vendor-mindmap`; this stage did not change code splitting.

## Browser QA

- Script: `.ai/tasks/2026-06-05-agent-artifact-rail-mcp-shortcut/qa-artifact-rail-mcp-shortcut.cjs`
- URL: `http://127.0.0.1:5173/worldline/agent`
- Result: passed.
- Assertions covered:
  - `ARTIFACT RAIL` is visible.
  - Artifact Rail item-level `Copy MCP` is visible.
  - Clicking Artifact Rail `Copy MCP` triggers a visible `MCP read call` status.
  - The visible status is local to `.artifact-panel .artifact-mcp-message`.
- Screenshot: `.ai/tasks/2026-06-05-agent-artifact-rail-mcp-shortcut/screenshots/artifact-rail-copy-mcp.png`

## Visual QA

- Screenshot checked: Artifact Rail shows local copy status above the artifact list.
- Both visible artifact rows keep their main focus button and separate `Copy MCP` button.
- No incoherent overlap was observed across the right rail content.

## Iteration Note

- Initial screenshot showed the Artifact Rail action writing status to the left Replay Export Registry message.
- Fixed by adding `artifactRailMessage` and `copyArtifactRailMcpCall`, while preserving the shared MCP instruction helper.

## Temporary Browser Cleanup

- Started a dedicated Chrome CDP instance on port `9349` with task-local profile `chrome-profile`.
- Stopped Chrome processes whose command line referenced that profile.
- Removed the task-local `chrome-profile`; final existence check returned `False`.
