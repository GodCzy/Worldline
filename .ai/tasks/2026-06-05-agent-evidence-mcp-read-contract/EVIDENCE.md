# Evidence

## Planned Checks

- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py"`
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- `git diff --check -- src/services/worldline_agent_workflow_service.py src/services/worldline_run_ledger_service.py src/mcp/worldline_server.py test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-evidence-mcp-read-contract`
- Browser QA on `http://127.0.0.1:5173/worldline/agent`

## Results

## Backend pytest

Command:

`wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py -q"`

Result:

- Passed: `9 passed, 3 warnings in 88.61s`.
- Covered run ledger `list_evidence`, service manifest, `inspect_run_evidence`, evidence lookup, source lookup, and missing-source `not_found`.
- Initial parallel pytest attempts timed out because older pytest/uv processes and a long-running Vite dev server were still consuming WSL resources. Those task-scoped validation processes were stopped, then the focused suite passed.

## Frontend build

Command:

`wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`

Result:

- Passed: Vite built successfully in `1m 59s`.
- Existing warning remains: several chunks exceed 500 kB after minification.
- Initial parallel build failed at Less preprocessing with `timed-out`; single-process retry passed.

## Diff check

Command:

`git diff --check -- src/services/worldline_agent_workflow_service.py src/services/worldline_run_ledger_service.py src/mcp/worldline_server.py test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-evidence-mcp-read-contract`

Result:

- Passed.
- Warning only: `src/mcp/worldline_server.py` CRLF will be replaced by LF when Git touches it.

## Browser QA

Target:

`http://127.0.0.1:5173/worldline/agent`

Script:

`D:\dev\Worldline\.ai\tasks\2026-06-05-agent-evidence-mcp-read-contract\qa-evidence-mcp-cdp.mjs`

Result:

- Passed via Chrome CDP on port `9388`.
- Selected gate: `gate-evidence`.
- Evidence Copy MCP preview:
  - URI: `worldline-run-ledger://run-agent-workbench-preview/evidence/ev-worldline-contract`
  - Args include `evidence_id: ev-worldline-contract`.
  - Last MCP Call panel shows `worldline.inspect_run_evidence`.
- Source Copy MCP preview:
  - URI: `worldline-run-ledger://run-agent-workbench-preview/sources/source-worldline-knowledge-router`
  - Args include `source_id: source-worldline-knowledge-router`.
  - Last MCP Call panel shows `worldline.inspect_run_evidence`.

Screenshots:

- `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-evidence-mcp-read-contract\screenshots\focus-dossier-evidence-mcp.png`
- `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-evidence-mcp-read-contract\screenshots\focus-dossier-source-mcp.png`
