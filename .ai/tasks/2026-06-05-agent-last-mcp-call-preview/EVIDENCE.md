# Evidence

## Planned Checks

- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-last-mcp-call-preview`
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
git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-last-mcp-call-preview
```

Result: passed with no output.

## Browser QA

Target: `http://127.0.0.1:5173/worldline/agent`

Flow:

1. Open Agent Workbench through Chrome CDP.
2. Select Run Preview event.
3. Open Replay Manifest to show Focus Dossier.
4. Click the first Focus Dossier artifact `Copy MCP` button using CDP mouse events.
5. Verify local Focus Dossier preview and global `LAST MCP CALL` preview.

Observed:

- Focus message: `MCP read call copied for Evidence dossier.`
- Focus local preview includes `worldline-run-ledger://run-agent-workbench-preview/artifacts/artifact-evidence-dossier`.
- Focus local preview args include `include_content: false` and `audit_db_id: ""`.
- Global last-call preview includes source `Focus Dossier`, tool `worldline.inspect_run_artifacts`, URI, and args.

Screenshots:

- `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-last-mcp-call-preview\screenshots\last-mcp-call-preview.png`
- `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-last-mcp-call-preview\screenshots\last-mcp-call-global-preview.png`
