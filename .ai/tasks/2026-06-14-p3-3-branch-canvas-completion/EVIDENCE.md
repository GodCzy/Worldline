# P3-3 Branch Canvas Completion Evidence

Date: 2026-06-14

## Current Baseline

- Branch: `codex/worldline-recovery-refactor`
- Initial status: clean worktree before this slice.
- Source of truth: `D:\dev\Worldline`

## Implementation Evidence

- `WorldlineWorkbenchService` now adds branch-level `routeTrace`, `gateRefs`, `quality.hints`, and an evidence-required policy.
- Evidence-free generation returns `needs_evidence` and no default branches.
- Branch Inspector now displays support status, support hints, gate refs, and route trace.
- Branch Canvas emits preview on hover/focus and has mobile-contained scroll behavior.

## Validation

### Backend

- `wsl.exe -d Debian --cd /mnt/d/dev/Worldline -- .venv/bin/python -m py_compile src/services/worldline_workbench_service.py test/test_worldline_live_services.py`
  - Result: passed.
- `wsl.exe -d Debian --cd /mnt/d/dev/Worldline -- .venv/bin/python -m pytest test/test_worldline_live_services.py -k workbench -s`
  - Result: passed, `2 passed, 6 deselected`.
- `wsl.exe -d Debian --cd /mnt/d/dev/Worldline -- .venv/bin/python -m ruff check src/services/worldline_workbench_service.py test/test_worldline_live_services.py`
  - Result: passed.

### Frontend

- Vue SFC parse/template/style check with `@vue/compiler-sfc`
  - Files: `WorldlineBranchCanvas.vue`, `WorldlineBranchDetailPanel.vue`, `WorldlineBranchNode.vue`, `WorldlineGraphFocusPanel.vue`, `WorldlineWorkbenchView.vue`.
  - Result: passed, `validated 5 Vue SFC files`.
- `wsl.exe -d Debian --cd /mnt/d/dev/Worldline/web -- /home/joy/.hermes/node/bin/node node_modules/vite/bin/vite.js build`
  - Result: passed.
  - Note: existing large chunk warning remains; no new build failure.

### Browser QA

- Dynamic Browser tools were not exposed in this session after tool discovery, so the visual pass used local static QA plus Edge CDP.
- Static QA server:
  - `qa_static_server.py --dist D:\dev\Worldline\web\dist --host 127.0.0.1 --port 5183`
  - API stubs covered `/api/system/info`, `/api/auth/me`, `/api/knowledge/.../worldline/overview`, and `/api/knowledge/.../worldline/generate`.
- CDP QA:
  - `qa_headless_check.mjs`
  - Report: `p3-3-branch-canvas-browser-qa.json`.
  - Screenshots: `p3-3-worldline-branch-canvas-cdp-1440x900.png`, `p3-3-worldline-branch-canvas-cdp-390x844.png`.
  - Output directory default was verified without `QA_OUT_DIR`; artifacts land in this task directory.
  - Result: desktop and mobile both rendered the branch canvas, inspector, route trace, support status, gate refs, and evidence rail.
  - Overflow: no page-level horizontal overflow at `1440x900` or `390x844`; mobile canvas overflow is contained inside the canvas scroller.

### P3 Regression Evidence

- `wsl.exe -d Debian --cd /mnt/d/dev/Worldline -- .venv/bin/python -m pytest test/test_worldline_run_audit_contract.py -s`
  - Result: passed.
- `wsl.exe -d Debian --cd /mnt/d/dev/Worldline -- .venv/bin/python -m pytest test/test_worldline_phase6_7_release_gate.py -s`
  - Result: passed, `5 passed`.
- Combined rerun:
  - `wsl.exe -d Debian --cd /mnt/d/dev/Worldline -- .venv/bin/python -m pytest test/test_worldline_run_audit_contract.py test/test_worldline_phase6_7_release_gate.py -s`
  - Result: passed, `6 passed`.

### Docs And Release Checks

- `wsl.exe -d Debian --cd /mnt/d/dev/Worldline -- /home/joy/.hermes/node/bin/node node_modules/vitepress/bin/vitepress.js build docs`
  - Result: passed.
- `docker compose config`
  - Windows side result: `docker` command not found.
  - WSL Debian fallback: passed and rendered the compose configuration.
- `git diff --check`
  - Result: passed.

### Notes

- Windows Node was not used for production build because the checked-in `node_modules` is Linux-shaped and missing Windows Rollup optional native packages.
- WSL `node` was not on PATH in this shell; the validated build path used Hermes' Linux Node at `/home/joy/.hermes/node/bin/node`.
- Temporary static QA service was stopped after CDP verification.
- Full legacy run-ledger suite was not used as P3 acceptance evidence; the focused audit contract, phase release-gate tests, existing real E2E evidence, and code-level API audit cover the P3 ledger/replay acceptance boundary for this closeout.
