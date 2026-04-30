# phase-42-v1.2-real-backend-acceptance-smoke

## Date

- 2026-03-22

## Baseline

- controller start HEAD: `433a66f docs(worldline): add docker startup and response rules`
- v1.2 workbench implementation baseline: `c58f0f6 feat(worldline): finish v1.2 workbench first-wave`

## Task

- continue the v1.2 acceptance round
- verify `/worldline/poe` and `/worldline/unknown` against the real Docker backend
- if the backend could not run, only locate the minimal missing support and do not expand unrelated scope

## MCP Judgment

- MCP remains relevant in this phase
- Playwright-class browser automation is a real acceptance accelerator for the workbench route and fail-closed route
- this round used real browser automation against the running Docker stack instead of mock backend smoke

## Actual Subagent Decomposition

### Read-only wave

- `system_mapper`
  - confirmed that `/worldline/:themeId` is routed by [index.js](D:/worldline/web/src/router/index.js) into [WorldlineWorkbenchView.vue](D:/worldline/web/src/views/worldline/WorldlineWorkbenchView.vue)
  - confirmed that `/worldline` still lands on [WorldlineHubView.vue](D:/worldline/web/src/views/worldline/WorldlineHubView.vue)
  - isolated the real dependency chain for this round as `infoStore.loadInfoConfig() -> /api/system/info`
  - separated public layout noise from workbench-local behavior
- `product_architect`
  - set the minimal backend acceptance boundary to `GET /api/system/health` and `GET /api/system/info`
  - explicitly rejected any backend expansion beyond keeping those public interfaces alive for this round
- `qa_release_auditor`
  - defined the minimum smoke gate for `/worldline/poe` and `/worldline/unknown`
  - classified guest-mode knowledge/admin/agent 401s as tolerable noise if the workbench body remains usable
- `Zeno` as read-only backup
  - reinforced that this round should judge `poe` success, `unknown` fail-closed correctness, and whether route/layout noise is blocking

## Runtime Reality Check

- Docker stack was already running locally
- `docker compose ps` showed `api-dev` healthy on `5050` and `web-dev` available on `5173`
- `GET http://127.0.0.1:5050/api/system/health` returned `200`
- `GET http://127.0.0.1:5050/api/system/info` returned `200`
- real `system/info` payload still exposes the `poe` theme and current branding data
- `api` logs showed stable startup and successful `system/info` / `system/health` responses
- the historical `WorldlineHubView.vue` import parse error found in old `web-dev` logs did not reproduce in the current runtime smoke

## Smoke Result

### `/worldline/poe`

- passed
- the page rendered the workbench body under the real Docker backend
- visible elements included:
  - `世界线工作台`
  - PoE theme identity: `流放之路 / Path of Exile`
  - question input area
  - branch main stage
  - detail panel
  - evidence rail
  - next-step panel
- the first-layer workbench still rendered `3 条分支`
- selecting `闪电箭锐眼刷图候选` updated the focused state
- clicking `沿这条主线继续生成` advanced the workbench to round 2 and rendered the next-layer branches
- clicking `带着这条线继续对话` in guest mode redirected to `/login`
- no blocking `4xx/5xx` responses were observed on the workbench-critical path
- no page-level runtime exception blocked rendering

### `/worldline/unknown`

- passed
- the page entered fail-closed state instead of silently falling back to PoE data
- visible unsupported copy included:
  - `UNSUPPORTED THEME`
  - `主题 unknown 尚未接入世界线适配器`
- no PoE worldline branch copy such as `SRS 死灵师` / `闪电箭锐眼` / `碎骨勇士` was rendered on the `unknown` route

## Remaining Noise

- guest-mode public layout still triggers non-blocking unauthorized requests from shared shells, especially:
  - knowledge database list loading in [AppLayout.vue](D:/worldline/web/src/layouts/AppLayout.vue)
  - agent initialization and chat prefetch when entering theme chat from [WorldlineWorkbenchView.vue](D:/worldline/web/src/views/worldline/WorldlineWorkbenchView.vue)
- these show up as `用户未登录` console errors or warnings
- they did not prevent:
  - workbench rendering
  - fail-closed rendering
  - guest redirect to `/login`
- therefore they are acceptance-noise, not a blocker for the current v1.2 first-wave workbench

## Code Change Judgment

- no product source patch was required in this round
- the real backend already satisfied the minimum runtime surface for v1.2 workbench acceptance
- the current stable output of this task is the acceptance record itself

## Phase Judgment

- current phase: `v1.2 workbench first-wave real-backend acceptance`
- readiness for next phase: `ready`
- main remaining gap before advancing:
  - decide whether guest-mode public-shell auth noise should be cleaned before broader module expansion
  - then either run a dedicated noise-reduction pass or start the next adapter expansion phase
