# Evidence

## Planned Checks

- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py -q"`
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- `git diff --check -- server/routers/worldline_run_router.py src/services/worldline_agent_workflow_service.py test/test_worldline_run_ledger_service.py web/src/apis/worldline_api.js web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-run-manifest-api-inspector`
- Browser QA on `http://127.0.0.1:5173/worldline/agent`

## Results

## Backend Contract

Command:

`wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py -q"`

Result:

- Pass: `11 passed, 3 warnings in 128.40s`.
- Covered `GET /api/worldline/runs/{run_id}/manifest` for existing and missing runs.
- Warnings are pre-existing SQLAlchemy/Pydantic deprecations and a `requests` dependency warning.

## Frontend Build

Command:

`wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`

Result:

- Pass: Vite production build completed in 1m 55s.
- Warning: existing large bundle chunks over 500 kB for vendor packages.

## Diff Check

Command:

`git diff --check -- server/routers/worldline_run_router.py src/services/worldline_agent_workflow_service.py test/test_worldline_run_ledger_service.py web/src/apis/worldline_api.js web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-run-manifest-api-inspector`

Result:

- Pass.

## Browser QA

Target:

`http://127.0.0.1:5173/worldline/agent`

Script:

`D:\dev\Worldline\.ai\tasks\2026-06-05-agent-run-manifest-api-inspector\qa-manifest-api-inspector-cdp.mjs`

Result:

- Pass: CDP QA loaded the Agent Workbench.
- Pass: CDP injected temporary admin store state for QA only; no real token or account was written.
- Pass: CDP Fetch fulfilled mocked run save and mocked manifest API responses.
- Pass: captured frontend request `GET /api/worldline/runs/run-agent-workbench-api/manifest?include_resources=true&limit=50`.
- Pass: UI rendered Backend Manifest `Loaded`, 18 resources, 5 read tools, and sample `worldline-run-ledger://` resources.
- Screenshot: `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-run-manifest-api-inspector\screenshots\run-manifest-api-inspector.png`

## Runtime State

- Temporary Chrome CDP profile was removed after QA.
- Vite dev server remains running at `http://127.0.0.1:5173/` for manual inspection.
