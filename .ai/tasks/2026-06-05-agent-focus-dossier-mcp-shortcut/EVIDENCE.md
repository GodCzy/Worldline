# Evidence

## Planned Checks

- `npm --prefix web run build`
- `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-focus-dossier-mcp-shortcut`
- Browser QA on `http://127.0.0.1:5173/worldline/agent`

## Results

## Build

Command:

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"
```

Result: passed. Vite emitted the existing large chunk warning for vendor bundles.

## Diff Check

Command:

```powershell
git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-focus-dossier-mcp-shortcut
```

Result: passed with no output.

## Browser QA

Target: `http://127.0.0.1:5173/worldline/agent`

Flow:

1. Open Agent Workbench through Chrome CDP.
2. Select Run Preview event.
3. Open Replay Manifest to show Focus Dossier.
4. Click the first Focus Dossier artifact `Copy MCP` button using CDP mouse events.

Observed:

- Focus Dossier title: `Agent Workbench Stage 1`
- Focus Dossier artifact MCP buttons: `4`
- Message after click: `MCP read call copied for Evidence dossier.`

Screenshot:

`D:\dev\Worldline\.ai\tasks\2026-06-05-agent-focus-dossier-mcp-shortcut\screenshots\focus-dossier-copy-mcp.png`

Note: a first `element.click()` probe did not surface the message because it did not behave like a focused browser gesture for clipboard flow. The follow-up CDP mouse event check passed.
