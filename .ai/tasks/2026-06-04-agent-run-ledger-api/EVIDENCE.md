# Evidence

## Initial State

- Active root: `D:\dev\Worldline`.
- Prior Stage 1 added a local `/worldline/agent` preview and frontend API wrappers for future `/api/worldline/runs`.
- Existing worktree was already dirty from previous Worldline recovery and frontend/backend audit work.

## Commands

- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && python3 -m py_compile src/services/worldline_run_ledger_service.py server/routers/worldline_run_router.py server/routers/__init__.py"`: passed.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && uv run --group test pytest test/test_worldline_run_ledger_service.py"`: failed before test execution because `uv` attempted to download `grpcio-tools==1.78.0` from the configured Tsinghua PyPI mirror and hit `tls handshake eof`.
- Removed the failed `D:\dev\Worldline\.venv` after confirming the path was inside the project root.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && docker compose exec -T api python -m pytest test/test_worldline_run_ledger_service.py"`: passed, `2 passed, 3 warnings in 15.38s`.
- `git diff --check`: passed; only existing CRLF replacement warnings were emitted.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && docker compose config"`: passed.
- `wsl -d Debian -- bash -lc "curl -fsS http://127.0.0.1:5050/api/system/health"`: initially timed out while `uvicorn --reload` was waiting for old connections to close; after `docker compose restart api`, returned `{"status":"ok","message":"服务正常运行"}`.
- OpenAPI route check after API restart listed:
  - `/api/worldline/runs`
  - `/api/worldline/runs/{run_id}`
  - `/api/worldline/runs/{run_id}/events`
  - `/api/worldline/runs/{run_id}/branches/{branch_id}/approve`
  - `/api/worldline/runs/{run_id}/branches/{branch_id}/reject`
  - `/api/worldline/runs/{run_id}/skills/propose`
- Unauthenticated `POST /api/worldline/runs` returned `401` with `{"detail":"请登录后再访问"}`.

## Results

- Added `src/services/worldline_run_ledger_service.py`.
- Added `server/routers/worldline_run_router.py`.
- Registered the router in `server/routers/__init__.py`.
- Added `test/test_worldline_run_ledger_service.py`.
- The service can create runs, persist to JSON, reload runs, approve/reject branches, list events, and add skill proposals.
- The router exposes the Stage 2 contract under `/api/worldline/runs` and requires authenticated/admin access.

## Residual Risk

- Stage 2 uses `config.save_dir/worldline/runs.json` and does not yet use Postgres migrations.
- Route-level tests use dependency override and tmp storage; live authenticated API create/approve was not run because no admin credentials were needed for this focused pass.
- The previous broad worktree dirtiness remains and was not reverted.
- Host `uv run` remains vulnerable to the configured Tsinghua PyPI mirror TLS failures; container pytest was used for focused verification.
