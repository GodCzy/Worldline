# Home, Theme, Auth Fix Evidence

Updated: 2026-06-03

## Static Checks

- Old demo keyword scan: no matches in the current frontend, docs, task evidence, tests, scripts, or services after cleanup.
- Login route scan:
  - No direct `router.push('/login')` calls in `web/src`.
  - No direct `router.push("/login")` calls in `web/src`.
  - No old session redirect handoff remains in `web/src`.
- `git diff --check`: passed; Git reports CRLF normalization warnings for a few Windows-edited files only.
- Repeated global CSS import check:
  - Removed the duplicate `main.css` import from `web/src/components/AgentChatComponent.vue`.
  - Reason: `main.css` is already loaded once in `web/src/main.js`; importing it again inside scoped Less made production CSS transformation extremely slow.

## Account And Database

- Local Postgres was fixed by moving the database data path in `docker-compose.override.yml` to a Docker named volume.
- `docker compose ps postgres`: service is healthy.
- Joy account verification:
  - `username = Joy`
  - `user_id = Joy`
  - `role = superadmin`
  - `is_deleted = 0`
  - `password_hash_format_ok = true`
- Plaintext password was not written to repo files, screenshots, or reports.

## Build And Gate

- `cd web && npm run build`: passed in 4m32s after removing the duplicate scoped global CSS import.
- `npm run docs:build`: passed.
- `docker compose config`: passed.
- `python3 scripts/worldline_phase6_7_release_gate.py --output .ai/tasks/2026-06-03-home-theme-auth-fix/release-gate-report.json`: passed, 6/6 checks.

## Playwright Screenshots

- Script: `.ai/tasks/2026-06-03-home-theme-auth-fix/screenshot-ui.cjs`
- Report: `.ai/tasks/2026-06-03-home-theme-auth-fix/screenshots/ui-screenshot-report.json`
- Result: 15 screenshot checks passed, `failures=[]`.
- Latest screenshot run: 2026-06-03T15:15:45Z.
- Latest release gate run after screenshots: 2026-06-03T15:15:59.
- Pages:
  - `/`
  - `/themes`
  - `/worldline`
  - unauthenticated `/agent` redirect to `/?login=1&redirect=/agent`
  - mocked Joy superadmin sidebar
- Viewports:
  - `1920x1080`
  - `1440x900`
  - `390x844`

## Backend Pytest

- `uv run --no-sync pytest ...` did not run because the current `.venv` had no `pytest`.
- `UV_INDEX_URL=https://pypi.org/simple uv run --group test pytest ...` did not run because dependency sync failed while downloading `zstandard==0.25.0` with a TLS handshake EOF.
- The failed dependency sync created a partial `.venv`; it was removed after path verification.
- Retry after network/package-source recovery:
  - `uv run --group test pytest test/test_knowledge_object_models.py test/test_worldline_live_services.py test/test_evidence_service.py test/test_worldline_phase6_7_release_gate.py`

## Final Summary

- OutputMD summary: `D:\document\OutputMD\2026-06-03-worldline-home-theme-auth-fix.md`
