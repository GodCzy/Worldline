# Evidence

## Planned Checks

- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py::test_worldline_run_router_exposes_stage2_contract -q"`
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py -q"`
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- `git diff --check -- src/services/worldline_run_ledger_service.py server/routers/worldline_run_router.py test/test_worldline_run_ledger_service.py web/src/apis/worldline_api.js web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-06-agent-run-selector`
- Browser QA on `http://127.0.0.1:5173/worldline/agent`

## Results

- `git diff --check -- src/services/worldline_run_ledger_service.py server/routers/worldline_run_router.py test/test_worldline_run_ledger_service.py web/src/apis/worldline_api.js web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-06-agent-run-selector`
  - Passed with no output.
  - Note: several Worldline files in this branch are still untracked, so git only reports tracked diff stats for `web/src/apis/worldline_api.js`.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py::test_worldline_run_router_exposes_stage2_contract -q"`
  - Passed: `1 passed, 3 warnings in 287.00s`.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py -q"`
  - Passed: `11 passed, 3 warnings in 298.24s`.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
  - Passed: built in `6m 22s`.
  - Existing Vite warning remains: some chunks exceed 500 kB after minification.
- Browser QA:
  - Script: `D:\dev\Worldline\.ai\tasks\2026-06-06-agent-run-selector\qa-run-selector-cdp.mjs`
  - Captured requests:
    - `GET http://127.0.0.1:5173/api/worldline/runs?limit=8`
    - `GET http://127.0.0.1:5173/api/worldline/runs/run-agent-selector-loaded`
    - `GET http://127.0.0.1:5173/api/worldline/runs/run-agent-selector-loaded/artifacts`
  - Screenshot: `D:\dev\Worldline\.ai\tasks\2026-06-06-agent-run-selector\screenshots\run-selector-loaded.png`
  - Temporary Chrome CDP profile was removed after QA.
