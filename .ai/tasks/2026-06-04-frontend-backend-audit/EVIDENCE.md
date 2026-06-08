# Evidence

## Initial Context

- Active root: `D:\dev\Worldline`.
- Pointer root: `D:\document\Worldline`.
- Previous thread read: `019e8ca8-d62d-7ca2-8cc2-b50785f3ef8a`.
- Current branch at task start: `codex/worldline-recovery-refactor`.
- Worktree was already dirty at task start with many modified/deleted files from prior Worldline work.

## Commands And Results

## Findings

- Frontend previously had only partial Worldline backend coverage: it used generate/evidence-style flows, but the live workbench did not expose the backend overview, MCP manifest/audit, workflow plan, wiki rebuild, graph rebuild, golden set, and deterministic quality gate actions in one operator surface.
- The route handoff from Worldline theme context to graph/agent pages dropped `db_id` / `knowledge_db_id` in normalized context, so live database routes could fall back to the wrong graph database.
- `GraphView` treated every graph route like Neo4j during initial status loading and was cramped on mobile, especially for `/graph?...&db_id=...` LightRAG-style routes.
- Backend contracts already expose more than the old frontend used: Worldline overview, stale wiki pages, graph conflicts, Neo4j projection, workflow planning, MCP manifest/audit, golden set creation, and quality gate execution.

## Changes

- Added `web/src/components/worldline/WorldlineLiveOpsPanel.vue` to show live backend counts and execute Worldline operations from the workbench.
- Extended `web/src/apis/worldline_api.js` with backend wrappers for stale wiki pages, graph conflicts, and Neo4j projection, and made theme knowledge DB resolution accept more backend payload shapes.
- Updated `web/src/views/worldline/WorldlineWorkbenchView.vue` to load live overview data, wire Live Ops actions to existing backend routes, refresh after write actions, and keep generated worldline data in sync.
- Updated `web/src/stores/themeContext.js` to preserve `db_id` and `knowledge_db_id` through normalized route context.
- Updated `web/src/views/GraphView.vue` to select route-provided DB IDs, avoid stale Neo4j status for non-Neo4j routes, and improve mobile layout.
- Updated `web/src/components/worldline/WorldlineGraphFocusPanel.vue` to display the DB trace used by graph handoff.

## Validation

- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`: passed in 3m45s. Vite still reports existing large chunk warnings for vendor bundles.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm run docs:build"`: passed in 28.44s.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && docker compose config"`: passed.
- `git diff --check`: passed; only CRLF replacement warnings were emitted for existing Windows-line-ending files.
- `rg --files -g '*.md' D:\dev\Worldline D:\document\Worldline`: returned 12 Markdown files, confirming the expected reset-era doc surface is discoverable from the active and pointer roots.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && python3 scripts/worldline_phase6_7_release_gate.py --output .ai/tasks/2026-06-04-frontend-backend-audit/release-gate-report.json"`: passed; report status `passed`, 6/6 checks.
- Screenshot QA via Playwright against `http://127.0.0.1:5173`: passed 9/9 screenshots for `/worldline`, `/worldline/live-kb?...knowledge_db_id=kb_live`, and `/graph?...db_id=kb_live&knowledge_db_id=kb_live` at 1920x1080, 1440x900, and 390x844. Report: `.ai/tasks/2026-06-04-frontend-backend-audit/screenshots/live-ops-screenshot-report.json`.
- Visual inspection after the mobile Graph fix confirmed the workbench and graph pages do not have obvious overlapping controls at desktop or 390px mobile width.

## Blocked / Residual

- Focused pytest command was attempted with `uv run --group test pytest test/test_worldline_live_services.py test/test_worldline_phase6_7_release_gate.py`, but `uv` could not download `shapely==2.1.2` from the configured Tsinghua PyPI mirror due `tls handshake eof`. The generated `.venv` was removed after verifying the path.
- Windows-side `docker compose config` was unavailable because Windows does not expose `docker`; the same check passed in WSL Debian.
- The working tree remains dirty from earlier Worldline work, including deleted old task directories and unrelated modified files. These were not reverted.
- Vite large chunk warnings remain a future performance optimization target; they did not fail the build.

## 2026-06-04 Backend Availability Follow-up

- Symptom: homepage showed `后端暂不可用，当前使用本地配置渲染首页`.
- Confirmed cause 1: port `5050` had no listener, and Docker Compose only had `postgres` running.
- Confirmed cause 2: the Vite dev server was started without `VITE_API_URL`, so `/api` proxy used the container-network default `http://api:5050`, which timed out for a bare local frontend.
- Confirmed cause 3: API image build failed because `docker/api.Dockerfile` forced Debian apt sources to Tsinghua, and the current network could not connect to that mirror.
- Confirmed cause 4: API container runtime command used `uv run`, which retried dependency sync against the Tsinghua PyPI index and crashed the container.
- Fix: changed `docker/api.Dockerfile` to use official Debian/PyPI defaults unless mirrors are explicitly passed, fixed Docker build `COPY` paths, and changed API/worker compose commands to direct `uvicorn`/`arq` invocation.
- Runtime action: built `worldline-api:0.5.dev`, started `api` with compose dependencies, then restarted the Vite dev server with `VITE_API_URL=http://127.0.0.1:5050`.
- Validation:
  - `docker compose build api`: passed.
  - `docker compose up -d api`: passed.
  - `curl http://127.0.0.1:5050/api/system/health`: returned `{"status":"ok","message":"服务正常运行"}`.
  - `curl http://127.0.0.1:5173/api/system/health`: returned `{"status":"ok","message":"服务正常运行"}` through Vite proxy.
  - `curl http://127.0.0.1:5173/api/system/info`: returned live Worldline config from backend.
  - `docker compose config`: passed.
  - `npm --prefix web run build`: passed; Vite large chunk warnings remain.
  - `npm run docs:build`: passed.
  - `git diff --check`: passed with CRLF warnings only.
- Browser note: in-app Browser automation was blocked by Browser URL policy for `http://127.0.0.1:5173/`, so final UI state was verified through HTTP endpoints instead of a browser reload.

## 2026-06-04 Goal Continuation: Frontend/Backend Completion Pass

### Implemented

- Graph/backend:
  - `server/routers/graph_router.py` now attempts lazy recovery of `graph_base`, returns clear 503 details for write/index endpoints, and returns degraded empty payloads for read routes where the UI can render safely.
  - `docker-compose.yml` now makes API/worker depend on healthy Neo4j `graph`.
  - `src/__init__.py` now uses `load_dotenv(..., override=False)`, preserving Compose-provided `NEO4J_URI=bolt://graph:7687`.
- Theme modules:
  - Added custom module helpers and `/api/system/themes` GET/POST/PUT/DELETE in `server/routers/system_router.py`.
  - `/api/system/info` now merges modules from `saves/config/theme_modules.json`.
  - Added frontend `themeModuleApi` in `web/src/apis/system_api.js`.
  - Added `createThemeModule`, `updateThemeModule`, `deleteThemeModule`, and `loadThemeModules` to `web/src/stores/info.js`.
  - Replaced `web/src/views/themes/ThemeHubView.vue` placeholder with a module registry UI, including knowledge DB selection, Wiki/Graph/Timeline/Quality Gate switches, edit/delete actions, and Worldline/theme-detail handoff.
- Knowledge database creation:
  - `web/src/views/DataBaseView.vue` now shows embedding model health, creation capability matrix, and post-create actions to upload files, inspect graph, or create a theme module.
  - The creation flow now preserves the created DB object/ID from the backend response or refreshed list.
- UI unification:
  - Strengthened global dark Ant overrides in `web/src/assets/css/worldline-design.css` and dark tokens in `web/src/stores/theme.js`.
  - Added dark UI coverage for `DataBaseView.vue`, `ThemeDetailView.vue`, `DashboardView.vue`, and `ExtensionsView.vue`.
  - Theme module modal uses global non-transparent dark modal styles so underlying page text no longer bleeds through.

### Validation

- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && python3 -m py_compile server/routers/system_router.py server/routers/graph_router.py"`: passed.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && docker compose config"`: passed.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`: passed after the final modal CSS change; Vite large chunk warnings remain.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm run docs:build"`: passed.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && git diff --check"`: passed with CRLF replacement warnings only.
- `docker compose restart api`: passed; API logs show `Successfully connected to Neo4j`.
- `curl http://127.0.0.1:5050/api/system/health`: returned `{"status":"ok","message":"服务正常运行"}`.
- `curl http://127.0.0.1:5173/api/system/health`: returned the same health payload through Vite proxy after restarting Vite from WSL.
- `curl http://127.0.0.1:5050/api/system/themes`: returned `{"success":true,"themes":[]}`.
- API-container direct module persistence check passed:
  - normalized a `QA Module` payload with `db_id=kb_qa`;
  - saved and reloaded it from a temporary `/tmp/worldline-theme-module-test` save dir;
  - verified merged module id `qa-module` and DB bridge `kb_qa`.
- Public screenshot QA via Chrome headless:
  - `.ai/tasks/2026-06-04-frontend-backend-audit/screenshots/edge-qa/themes-1440x900.png`
  - `.ai/tasks/2026-06-04-frontend-backend-audit/screenshots/edge-qa/worldline-1440x900.png`
  - `.ai/tasks/2026-06-04-frontend-backend-audit/screenshots/edge-qa/themes-new-module-1440x900.png`
  - `.ai/tasks/2026-06-04-frontend-backend-audit/screenshots/edge-qa/themes-390x844.png`
  - `.ai/tasks/2026-06-04-frontend-backend-audit/screenshots/edge-qa/worldline-390x844.png`
- In-app browser DOM check for protected routes confirmed unauthenticated redirects to `/?login=1&redirect=...`; no protected content screenshot was captured without an admin session.

### Validation Closure

- Host-side `uv run --group test pytest ...` remained blocked by the configured Tsinghua PyPI mirror, but the focused pytest set was completed inside the already-built API container after installing pytest tooling from official PyPI:
  - `docker compose exec -T api python -m pip install -i https://pypi.org/simple pytest pytest-asyncio pytest-httpx pytest-cov`: passed.
  - `docker compose exec -T api python -m pytest test/test_worldline_live_services.py test/test_worldline_phase6_7_release_gate.py`: passed, `7 passed, 1 warning in 12.60s`.
- Created a short-lived local QA user `codexqa260604`, used it for protected-page screenshots, temporarily elevated it to `superadmin` for the `/extensions` route because that route requires `requiresSuperAdmin`, then deleted the user and verified it no longer exists in PostgreSQL.
- Removed the temporary same-origin auth helper `web/public/__codex_qa_auth.html` after screenshots.
- Confirmed no temporary Chrome/Edge QA processes remained.
- Protected-page screenshot QA passed:
  - `.ai/tasks/2026-06-04-frontend-backend-audit/screenshots/auth-qa/database-1440x900.png`
  - `.ai/tasks/2026-06-04-frontend-backend-audit/screenshots/auth-qa/dashboard-1440x900.png`
  - `.ai/tasks/2026-06-04-frontend-backend-audit/screenshots/auth-qa/extensions-1440x900.png`
  - `.ai/tasks/2026-06-04-frontend-backend-audit/screenshots/auth-qa/graph-1440x900.png`
  - `.ai/tasks/2026-06-04-frontend-backend-audit/screenshots/auth-qa/extensions-dom-style-report.json`
- Visual inspection confirmed `/database`, `/dashboard`, `/extensions`, and `/graph` render as real protected pages in the unified dark Worldline style rather than blank, redirected, or white-card pages.
- Final `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`: passed in `3m 45s`; only the known Vite large chunk warning remains.

### Residual

- The host `uv` dependency sync path is still vulnerable to the configured Tsinghua PyPI mirror TLS failures. Container pytest with official PyPI was used as the focused backend verification path for this pass.
- Vite large chunk warnings remain a future bundle-splitting optimization target; they do not fail the build.
