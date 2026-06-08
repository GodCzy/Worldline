# Evidence

## Planned Checks

- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py::test_worldline_run_router_exposes_stage2_contract -q"`
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py -q"`
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- `git diff --check -- src/services/worldline_run_ledger_service.py server/routers/worldline_run_router.py test/test_worldline_run_ledger_service.py web/src/apis/worldline_api.js web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-06-agent-run-maintenance-audit`
- Browser QA on `http://127.0.0.1:5173/worldline/agent`

## Results

- PASS `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py::test_worldline_run_router_exposes_stage2_contract -q"`
  - Result: `1 passed, 3 warnings in 261.13s`.
  - Coverage: rename route, blank title validation, archive route, archived run listing, and missing run 404 behavior were included in the focused router contract test.
- PASS `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py -q"`
  - Result: `11 passed, 3 warnings in 265.37s`.
  - Coverage: run ledger service contracts, live-service collection guardrails, selector filters, cross-run compare, and maintenance audit events.
- PASS `git diff --check -- src/services/worldline_run_ledger_service.py server/routers/worldline_run_router.py test/test_worldline_run_ledger_service.py web/src/apis/worldline_api.js web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-06-agent-run-maintenance-audit`
  - Result: no whitespace errors.
- PASS `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
  - Result: Vite build completed in `5m 31s`.
  - Note: existing chunk size warnings remain for large vendor bundles (`vendor-g6`, `vendor-antdv`, etc.); no new build failure.
- PASS Browser QA with Chrome CDP:
  - Script: `.ai/tasks/2026-06-06-agent-run-maintenance-audit/qa-run-maintenance-cdp.mjs`.
  - Target: `http://127.0.0.1:5173/worldline/agent`.
  - Captured maintenance requests:
    - `POST /api/worldline/runs/run-maintenance-active/rename`
    - `POST /api/worldline/runs/run-maintenance-archive/archive`
  - Verified UI state:
    - Active run title updated to `Renamed Maintenance Run`.
    - Active ledger still points at `run-maintenance-active`.
    - Archive candidate row shows `archived`.
    - Archived row archive button is disabled.
  - Screenshot: `.ai/tasks/2026-06-06-agent-run-maintenance-audit/screenshots/run-maintenance-audit.png`.
  - Cleanup: isolated Chrome profile `.ai/tasks/2026-06-06-agent-run-maintenance-audit/chrome-profile-cdp` removed after QA.
