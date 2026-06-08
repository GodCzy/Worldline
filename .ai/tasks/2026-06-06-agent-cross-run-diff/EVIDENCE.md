# Evidence

## Planned Checks

- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py::test_worldline_run_router_exposes_stage2_contract -q"`
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py -q"`
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- `git diff --check -- src/services/worldline_run_ledger_service.py server/routers/worldline_run_router.py test/test_worldline_run_ledger_service.py web/src/apis/worldline_api.js web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-06-agent-cross-run-diff`
- Browser QA on `http://127.0.0.1:5173/worldline/agent`

## Results

- `git diff --check -- src/services/worldline_run_ledger_service.py server/routers/worldline_run_router.py test/test_worldline_run_ledger_service.py web/src/apis/worldline_api.js web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-06-agent-cross-run-diff`
  - Passed with no output.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py::test_worldline_run_router_exposes_stage2_contract -q"`
  - Passed: `1 passed, 3 warnings in 260.34s`.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py -q"`
  - Passed: `11 passed, 3 warnings in 264.86s`.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
  - Passed: built in `5m 26s`.
  - Existing Vite warning remains: some chunks exceed 500 kB after minification.
- Browser QA:
  - Script: `D:\dev\Worldline\.ai\tasks\2026-06-06-agent-cross-run-diff\qa-cross-run-diff-cdp.mjs`
  - First run failed only because the assertion expected lowercase `8 deltas` while CSS rendered uppercase `8 DELTAS`. The script was changed to compare case-insensitively.
  - Final run passed.
  - Captured requests:
    - `GET http://127.0.0.1:5173/api/worldline/runs?limit=8`
    - `GET http://127.0.0.1:5173/api/worldline/runs/run-cross-diff-left`
    - `GET http://127.0.0.1:5173/api/worldline/runs/run-cross-diff-left/artifacts`
    - `GET http://127.0.0.1:5173/api/worldline/runs/compare?left_run_id=run-cross-diff-left&right_run_id=run-cross-diff-right`
  - QA confirmed the active run stayed `run-cross-diff-left` after Compare.
  - Screenshot: `D:\dev\Worldline\.ai\tasks\2026-06-06-agent-cross-run-diff\screenshots\cross-run-diff-panel.png`
  - Temporary Chrome CDP profile was removed after QA.
