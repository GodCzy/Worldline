# Evidence

## Planned Checks

- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py -q"`
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- `git diff --check -- server/routers/worldline_run_router.py test/test_worldline_run_ledger_service.py web/src/apis/worldline_api.js web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-run-resource-drilldown`
- Browser QA on `http://127.0.0.1:5173/worldline/agent`

## Results

## Backend Contract

Command:

`wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py::test_worldline_run_router_exposes_stage2_contract -q"`

Result:

- Pass: `1 passed, 3 warnings in 293.50s`.
- Covers new HTTP drilldown routes for artifact, gate, evidence/source, knowledge, and missing resource 404.
- Note: initial shorter timeout attempts were insufficient because project import/collection can exceed 2 minutes.

Command:

`wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py -q"`

Result:

- Pass: `11 passed, 3 warnings in 206.53s`.
- Warnings are pre-existing SQLAlchemy/Pydantic deprecations and a `requests` dependency warning.

## Frontend Build

Command:

`wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`

Result:

- First run timed out at 244 seconds while Vite was still active; reran with a longer timeout.
- Pass: Vite production build completed in 4m 12s.
- Warning: existing large bundle chunks over 500 kB for vendor packages.

## Diff Check

Command:

`git diff --check -- server/routers/worldline_run_router.py test/test_worldline_run_ledger_service.py web/src/apis/worldline_api.js web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-run-resource-drilldown`

Result:

- Pass.

## Browser QA

Target:

`http://127.0.0.1:5173/worldline/agent`

Script:

`D:\dev\Worldline\.ai\tasks\2026-06-05-agent-run-resource-drilldown\qa-resource-drilldown-cdp.mjs`

Result:

- Pass: CDP QA loaded the Agent Workbench.
- Pass: CDP injected temporary admin store state for QA only; no real account credential was written.
- Pass: mocked run save and backend manifest responses.
- Pass: clicked `Inspect` on the backend manifest artifact resource.
- Pass: captured frontend request `GET /api/worldline/runs/run-agent-resource-drilldown/artifacts/read?artifact_id=replay-export-drilldown&include_content=true&limit=20`.
- Pass: UI rendered `Resource Detail`, `Loaded`, `worldline.inspect_run_artifacts`, and compact JSON response.
- Screenshot: `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-run-resource-drilldown\screenshots\run-resource-drilldown.png`

## Runtime State

- Temporary Chrome CDP profile was removed after QA.
- Vite dev server remains running at `http://127.0.0.1:5173/` for manual inspection.
