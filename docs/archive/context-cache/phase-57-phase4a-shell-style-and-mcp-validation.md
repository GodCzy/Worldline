# Phase 57 - Phase 4a shell style unification and redirect continuity

## Baseline

- Prior head: `c6545b2 docs(context-cache): update playwright mcp permission follow-up`
- Prior decision: Phase 4 can start conditionally; real-backend login interactive signoff remains known debt.
- This pass target:
  - verify Playwright MCP in a fresh run path (no `Transport closed`)
  - complete Phase 4a P0 minimal slice for style continuity + redirect continuity
  - keep scope limited to platform shell and auth/public handoff behavior

## Subagent decomposition (actually executed)

Read-only wave:

1. `system_mapper` (`019d4886-5834-7012-ad06-ab5302503700`)
   - produced Phase 4 first-wave minimal slice proposal (router + shell css + Home/Login)
2. `product_architect` (`019d4886-9058-77b3-9512-4451845e69a3`)
   - produced Phase 4a rules: platform fixed items / configurable items / interaction invariants
3. `qa_release_auditor` (`019d4886-73cc-79a0-8955-c93a437ab66c`)
   - completed shell + Playwright dual-channel acceptance with evidence path

Implementation wave:

4. `frontend_worker` (`019d488f-1210-70f0-b1dc-43527018bf1d`) was started but interrupted.
   - reason: generated encoding-corrupted Chinese strings in `HomeView.vue`
   - controller stopped worker, reverted polluted content, and finished implementation locally with minimal controlled edits.

## Code changes in this pass

1. `web/src/router/index.js`
   - centralized auth redirect helpers:
     - `normalizeAuthRedirect`
     - `setStoredRedirect`
     - `consumeStoredRedirect`
   - unauthenticated access now jumps to named route `login` with optional `?redirect=...`
   - logged-in visit to `/login` now resolves redirect in order:
     - query `redirect`
     - stored session redirect
     - fallback `/`

2. `web/src/assets/css/main.css`
   - added reusable platform shell primitives:
     - `.wl-shell`
     - `.wl-shell-topbar`
     - `.wl-brand`, `.wl-brand-logo`, `.wl-brand-text`
     - `.wl-nav-pills`, `.wl-nav-pill`
     - `.wl-shell-footer`, `.wl-shell-footer-inner`
   - purpose: reduce page-local duplicated topbar/footer/nav styling and provide shared visual language.

3. `web/src/views/HomeView.vue`
   - switched top bar/footer to shared shell semantic classes
   - nav pills now reuse shared pill classes
   - simplified `goToChat()` to `router.push('/agent')`; auth redirect now fully handled by router guard path

4. `web/src/views/LoginView.vue`
   - switched top bar/footer to shared shell semantic classes
   - footer links now reuse shared pill classes
   - `resolveRedirectPath()` now prioritizes `route.query.redirect`, then falls back to session storage

## Validation evidence

### Shell checks

- docker runtime and compose state checked; `web-dev`/`api-dev` serving on `5173/5050`
- health and route probes:
  - `http://127.0.0.1:5050/api/system/health` -> 200
  - `http://127.0.0.1:5173/worldline` -> 200
  - `http://127.0.0.1:5173/worldline/poe` -> 200
  - `http://127.0.0.1:5173/worldline/unknown` -> 200

### Build

- `npm run build` in `web/` passed after the patch
- chunk-size warnings remain non-blocking

### MCP Playwright

- fresh flow in this session succeeded:
  - `browser_close` -> `browser_navigate` -> `browser_take_screenshot`
  - no `Transport closed` surfaced
- screenshot evidence copied to repo artifacts:
  - `artifacts/playwright-mcp-phase4a-postchange/phase4a-post-worldline.png`
  - `artifacts/playwright-mcp-phase4a-postchange/phase4a-post-worldline-poe.png`
  - `artifacts/playwright-mcp-phase4a-postchange/phase4a-post-worldline-unknown.png`

## Known debt and risk

- `graph` container still reported unhealthy in compose status (not blocking this minimal route/style acceptance, but blocks graph capability signoff).
- real-backend login interactive chain signoff remains deferred debt.
- build chunk warnings indicate later optimization work, not a Phase 4a blocker.

## Phase judgment

- Current phase: `Phase 4a (shell continuity + protocol-safe expansion baseline)`
- Readiness for next phase: `conditionally ready`
- Main gap before advancing to broader 4b:
  - close graph service health issue
  - replay full real-backend interactive login handoff signoff with stable evidence
