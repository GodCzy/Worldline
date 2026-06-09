# P3-6 Evidence

Evidence will be appended as implementation and validation proceed.

## Backend Focused Tests

- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --group test pytest test/test_worldline_live_services.py::test_quality_gate_intentional_failure_has_replay_refs"`: passed.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --group test pytest test/test_worldline_live_services.py::test_quality_gate_builds_golden_set_and_replay test/test_worldline_live_services.py::test_quality_gate_intentional_failure_has_replay_refs"`: 2 passed, 1 SQLAlchemy deprecation warning.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --group test pytest test/test_worldline_live_services.py"`: 7 passed, 1 SQLAlchemy deprecation warning.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --group test pytest test/test_worldline_phase6_7_release_gate.py"`: 3 passed, 1 SQLAlchemy deprecation warning.

## Frontend Static Checks

- `@vue/compiler-sfc` parse/compile for `WorldlineBranchDetailPanel.vue`, `WorldlineLiveOpsPanel.vue`, and `WorldlineWorkbenchView.vue`: passed.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline/web && node node_modules/vite/bin/vite.js build"`: passed in 4m 7s; Vite reported existing large chunk warnings for vendor bundles.
- `C:\Users\Joy\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe web\src\utils\__tests__\worldlineGraphFocus.spec.js`: passed; Node reported the existing module type warning.

## Browser QA

- Served the production `web/dist` build through Vite preview on WSL and accessed it from Windows Chrome through the WSL network IP.
- Playwright route-mocked admin auth, `/api/system/info`, Worldline overview/generate, and Quality Gate run payloads.
- Desktop replay panel rendered with `Quality Gate Replay`, `evidence_accuracy`, and all targets: Evidence, Wiki, Graph, Time, Run.
- Wiki target focused the EvidenceRail wiki tab: `wiki:wiki-page-1`.
- Run target displayed `Quality Gate replay run: gate-replay-ui.`
- Graph target routed to `/graph` with `focus_layer=graph`, `entity_id=entity-1`, and `evidence_id=ev-1`.
- Timeline target routed to `/graph` with `focus_layer=timeline`, `fact_id=fact-1`, and `evidence_id=ev-1`.
- 390px viewport had no horizontal overflow.
- Screenshots:
  - `.ai/tasks/2026-06-09-p3-6-quality-gate-replay/screenshots/p3-6-replay-desktop.png`
  - `.ai/tasks/2026-06-09-p3-6-quality-gate-replay/screenshots/p3-6-replay-mobile-390.png`
  - `.ai/tasks/2026-06-09-p3-6-quality-gate-replay/screenshots/p3-6-replay-mobile-390-panel.png`

## Other Checks

- `git diff --check`: passed.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && docker compose config >/tmp/worldline-compose-config-p3-6.txt && wc -l /tmp/worldline-compose-config-p3-6.txt"`: passed, 473 lines.
