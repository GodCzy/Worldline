# Evidence

## Planned Checks

- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py -q"`
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- `git diff --check -- src/services/worldline_agent_workflow_service.py src/services/worldline_run_ledger_service.py src/mcp/worldline_server.py test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-knowledge-mcp-read-contract`
- Browser QA on `http://127.0.0.1:5173/worldline/agent`

## Results

## Backend pytest

Command:

`wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py -q"`

Result:

- Passed: `10 passed, 3 warnings in 142.70s`.
- Covered run ledger `list_knowledge`, manifest contract, `inspect_run_knowledge`, `wiki`, `graph`, `timeline`, selected item lookup, and missing item `not_found`.

## Frontend build

Command:

`wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`

Result:

- Passed: Vite built successfully in `1m 57s`.
- Existing warning remains: several chunks exceed 500 kB after minification.

## Diff check

Command:

`git diff --check -- src/services/worldline_agent_workflow_service.py src/services/worldline_run_ledger_service.py src/mcp/worldline_server.py test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-knowledge-mcp-read-contract`

Result:

- Passed.
- Warning only: `src/mcp/worldline_server.py` CRLF will be replaced by LF when Git touches it.

## Browser QA

Target:

`http://127.0.0.1:5173/worldline/agent`

Script:

`D:\dev\Worldline\.ai\tasks\2026-06-05-agent-knowledge-mcp-read-contract\qa-knowledge-mcp-cdp.mjs`

Result:

- Passed via Chrome CDP on port `9389`.
- Selected branch: `branch-plan`.
- Wiki Copy MCP preview:
  - URI: `worldline-run-ledger://run-agent-workbench-preview/wiki/wiki-agent-os`
  - Args include `kind: wiki`, `item_id: wiki-agent-os`.
  - Last MCP Call panel shows `worldline.inspect_run_knowledge`.
- Graph Copy MCP preview:
  - URI: `worldline-run-ledger://run-agent-workbench-preview/graph/entity-worldline-run`
  - Args include `kind: graph`, `item_id: entity-worldline-run`.
  - Last MCP Call panel shows `worldline.inspect_run_knowledge`.
- Timeline Copy MCP preview:
  - URI: `worldline-run-ledger://run-agent-workbench-preview/timeline/tf-stage1`
  - Args include `kind: timeline`, `item_id: tf-stage1`.
  - Last MCP Call panel shows `worldline.inspect_run_knowledge`.

Screenshots:

- `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-knowledge-mcp-read-contract\screenshots\focus-dossier-wiki-mcp.png`
- `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-knowledge-mcp-read-contract\screenshots\focus-dossier-graph-mcp.png`
- `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-knowledge-mcp-read-contract\screenshots\focus-dossier-timeline-mcp.png`

## Cleanup

- Removed generated Chrome profile cache directories under:
  - `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-knowledge-mcp-read-contract\chrome-profile-cdp`
  - `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-evidence-mcp-read-contract\chrome-profile`
  - `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-evidence-mcp-read-contract\chrome-profile-cdp`
