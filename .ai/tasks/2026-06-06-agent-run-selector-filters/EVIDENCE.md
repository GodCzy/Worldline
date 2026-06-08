# Evidence

## Planned Checks

- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py::test_worldline_run_router_exposes_stage2_contract -q"`
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py -q"`
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- `git diff --check -- src/services/worldline_run_ledger_service.py server/routers/worldline_run_router.py test/test_worldline_run_ledger_service.py web/src/apis/worldline_api.js web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-06-agent-run-selector-filters`
- Browser QA on `http://127.0.0.1:5173/worldline/agent`

## Results

- `git diff --check -- src/services/worldline_run_ledger_service.py server/routers/worldline_run_router.py test/test_worldline_run_ledger_service.py web/src/apis/worldline_api.js web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-06-agent-run-selector-filters`
  - Passed with no output.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py::test_worldline_run_router_exposes_stage2_contract -q"`
  - Passed: `1 passed, 3 warnings in 265.87s`.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py -q"`
  - Passed: `11 passed, 3 warnings in 263.17s`.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
  - Passed: built in `5m 9s`.
  - Existing Vite warning remains: some chunks exceed 500 kB after minification.
- Browser QA:
  - Script: `D:\dev\Worldline\.ai\tasks\2026-06-06-agent-run-selector-filters\qa-run-selector-filters-cdp.mjs`
  - First run failed because the QA assertion expected the filtered result message after loading, but the UI correctly changes the selector message to the active run. The script now asserts filtered result before load and active run after load.
  - Final run passed.
  - Captured requests:
    - `GET http://127.0.0.1:5173/api/worldline/runs?limit=8&query=selector&status=ready&theme_id=agent-workbench&created_by=qa-admin`
    - `GET http://127.0.0.1:5173/api/worldline/runs/run-agent-selector-filtered`
    - `GET http://127.0.0.1:5173/api/worldline/runs/run-agent-selector-filtered/artifacts`
  - Screenshot: `D:\dev\Worldline\.ai\tasks\2026-06-06-agent-run-selector-filters\screenshots\run-selector-filters-loaded.png`
  - Temporary Chrome CDP profile was removed after QA.
