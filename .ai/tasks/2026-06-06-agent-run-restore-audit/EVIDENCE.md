# Evidence

## Planned Checks

- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py::test_worldline_run_router_exposes_stage2_contract -q"`
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py -q"`
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- `git diff --check -- src/services/worldline_run_ledger_service.py server/routers/worldline_run_router.py test/test_worldline_run_ledger_service.py web/src/apis/worldline_api.js web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-06-agent-run-restore-audit`
- Browser QA on `http://127.0.0.1:5173/worldline/agent`

## Results

- PASS `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py::test_worldline_run_router_exposes_stage2_contract -q"`
  - Result: `1 passed, 3 warnings in 261.21s`.
  - Coverage: route-level restore endpoint, archived listing before restore, restored approved listing after restore, missing restore 404, and event total with `run.restored`.
- PASS `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py -q"`
  - Result: `11 passed, 3 warnings in 261.81s`.
  - Coverage: service restore action, route contract, live service collection guardrails, existing run ledger contracts.
- PASS `git diff --check -- src/services/worldline_run_ledger_service.py server/routers/worldline_run_router.py test/test_worldline_run_ledger_service.py web/src/apis/worldline_api.js web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-06-agent-run-restore-audit`
  - Result: no whitespace errors, including the final QA script and evidence files.
- PASS `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
  - Result: Vite build completed in `5m 7s`.
  - Note: existing chunk size warnings remain for large vendor bundles; no new build failure.
- PASS Browser QA with Chrome CDP:
  - Script: `.ai/tasks/2026-06-06-agent-run-restore-audit/qa-run-restore-cdp.mjs`.
  - Target: `http://127.0.0.1:5173/worldline/agent`.
  - Captured restore request: `POST /api/worldline/runs/run-restore-archived/restore`.
  - Verified UI state:
    - Archived row initially exposes `Restore`.
    - Restore call updates candidate row to `ready`.
    - Restore button is replaced by `Archive`.
    - Active run remains `run-restore-active`.
  - Screenshot: `.ai/tasks/2026-06-06-agent-run-restore-audit/screenshots/run-restore-audit.png`.
  - Cleanup: isolated Chrome profile `.ai/tasks/2026-06-06-agent-run-restore-audit/chrome-profile-cdp` removed after QA.
