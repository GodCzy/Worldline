# Evidence

## 2026-06-05

- `git diff --check -- src/services/worldline_run_ledger_service.py server/routers/worldline_run_router.py test/test_worldline_run_ledger_service.py web/src/apis/worldline_api.js web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-replay-artifact-registry`
  - Result: passed; no whitespace conflict output.
- `uv run --group test pytest test/test_worldline_run_ledger_service.py`
  - Result: not executed on Windows because `uv` is not installed on the Windows PATH.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && uv run --group test pytest test/test_worldline_run_ledger_service.py"`
  - Result: blocked before test execution by PyPI mirror TLS handshake failure for `langgraph-cli`.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && .venv/bin/python -m pytest test/test_worldline_run_ledger_service.py"`
  - Result: passed; 2 tests passed in 136.95s.
  - Notes: existing SQLAlchemy/Pydantic/requests dependency warnings remain.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
  - Result: passed in 2m 56s.
  - Note: Vite still reports existing large chunk warnings for vendor bundles.
- `node .ai/tasks/2026-06-05-agent-replay-artifact-registry/qa-artifact-registry.cjs`
  - Result: passed through Chrome CDP on `http://127.0.0.1:5173/worldline/agent`.
  - Assertions: `REPLAY EXPORT`, `Save Artifact`, `Artifact`, disabled `Save Artifact` in local non-admin preview, Markdown preview still renders.

## Screenshots

- `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-replay-artifact-registry\screenshots\artifact-registry-local-preview.png`
