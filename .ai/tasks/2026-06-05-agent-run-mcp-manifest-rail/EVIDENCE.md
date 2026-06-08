# Evidence

## Planned Checks

- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py -q"`
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- `git diff --check -- src/services/worldline_agent_workflow_service.py src/mcp/worldline_server.py test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-run-mcp-manifest-rail`
- Browser QA on `http://127.0.0.1:5173/worldline/agent`

## Results

## Backend Contract

Command:

`wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py -q"`

Result:

- First attempt timed out after 124 seconds while the Vite dev server was still consuming CPU.
- Stopped the validation-related pytest/uv and Vite processes, then reran the same command.
- Pass: `11 passed, 3 warnings in 138.12s`.
- Warnings are pre-existing SQLAlchemy/Pydantic deprecations and a `requests` dependency warning.

## Frontend Build

Command:

`wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`

Result:

- Pass: Vite production build completed in 2m 3s.
- Warning: existing large bundle chunks over 500 kB for vendor packages.

## Diff Check

Command:

`git diff --check -- src/services/worldline_agent_workflow_service.py src/mcp/worldline_server.py test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-run-mcp-manifest-rail`

Result:

- Pass.
- Warning: `src/mcp/worldline_server.py` CRLF will be replaced by LF the next time Git touches it.

## Browser QA

Target:

`http://127.0.0.1:5173/worldline/agent`

Script:

`D:\dev\Worldline\.ai\tasks\2026-06-05-agent-run-mcp-manifest-rail\qa-run-manifest-cdp.mjs`

Result:

- Pass: CDP QA found `[data-run-mcp-manifest="true"]`.
- Pass: Run MCP Manifest panel displayed `Artifacts`, `Gates`, `Evidence`, `Sources`, `Wiki`, `Graph`, and `Time` sections.
- Pass: `Copy Run Manifest` populated Last MCP Call with `worldline.inspect_run_manifest`.
- Pass: copied args include `run_id: run-agent-workbench-preview`, `include_resources: true`, `limit: 50`.
- Screenshot: `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-run-mcp-manifest-rail\screenshots\run-mcp-manifest-rail.png`

## Runtime State

- Temporary Chrome CDP profile was removed after QA.
- Vite dev server remains running at `http://127.0.0.1:5173/` for manual inspection.
