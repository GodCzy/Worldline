# Evidence

## Planned Checks

- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && uv run --group test pytest test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py"`
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- `git diff --check -- src/services/worldline_agent_workflow_service.py src/services/worldline_run_ledger_service.py src/mcp/worldline_server.py test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-gate-mcp-read-contract`
- Browser QA on `http://127.0.0.1:5173/worldline/agent`

## Results

## Backend Tests

First attempt:

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && uv run --group test pytest test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py"
```

Result: did not enter tests. `uv` dependency sync failed while fetching `https://pypi.tuna.tsinghua.edu.cn/simple/langchain/` with `tls handshake eof`.

Second attempt:

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py"
```

Result: collection failed because `server` and `src` were not on `PYTHONPATH`.

Final command:

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py"
```

Result: passed, `8 passed, 3 warnings in 121.03s`.

Covered:

- `WorldlineRunLedgerService.list_gates`
- `WorldlineAgentWorkflowService.inspect_run_gates`
- `worldline.inspect_run_gates` manifest contract
- Existing run ledger router and artifact inspect behavior

## Frontend Build

Command:

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"
```

Result: passed. Vite emitted the existing large chunk warning for vendor bundles.

## Diff Check

Command:

```powershell
git diff --check -- src/services/worldline_agent_workflow_service.py src/services/worldline_run_ledger_service.py src/mcp/worldline_server.py test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-gate-mcp-read-contract
```

Result: passed with a CRLF normalization warning for `src/mcp/worldline_server.py`.

## Browser QA

Target: `http://127.0.0.1:5173/worldline/agent`

Flow:

1. Click Gate Panel `Copy MCP`.
2. Verify Gate Panel message and global `LAST MCP CALL`.
3. Open Run Preview Replay Manifest.
4. Click Focus Dossier gate `Copy MCP`.
5. Verify local Focus Dossier preview and global `LAST MCP CALL`.

Observed:

- Gate Panel message: `MCP read call copied for Permission risk.`
- Gate Panel last call tool: `worldline.inspect_run_gates`
- Gate Panel URI: `worldline-run-ledger://run-agent-workbench-preview/gates/gate-permission`
- Focus Dossier row: `Gate: Evidence coverage`
- Focus Dossier message: `MCP read call copied for Evidence coverage.`
- Focus Dossier local URI: `worldline-run-ledger://run-agent-workbench-preview/gates/gate-evidence`
- Args include `run_id`, `gate_id`, and `audit_db_id`.

Screenshots:

- `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-gate-mcp-read-contract\screenshots\gate-panel-copy-mcp.png`
- `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-gate-mcp-read-contract\screenshots\focus-dossier-gate-mcp.png`
