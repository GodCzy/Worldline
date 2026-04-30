# phase-43-v1.2-guest-shell-noise-reduction-pass1

## Date

- 2026-03-31

## Baseline

- start HEAD: `c46cc8d docs(context-cache): record v1.2 real-backend smoke acceptance`
- prior stable conclusion:
  - v1.2 workbench first wave had already passed real-backend smoke once
  - remaining issue was guest-mode public-shell auth noise on worldline routes

## Task

- run the v1.2 acceptance noise-reduction round
- identify guest-mode unauthorized requests triggered under public worldline routes
- reduce noise only on public worldline access
- avoid unrelated refactor and avoid broad backend work

## Controller-Side Mapping

- guest-mode noise on public worldline access was traced to two frontend triggers:
  - [AppLayout.vue](D:/worldline/web/src/layouts/AppLayout.vue)
    - `onMounted()` always called `getRemoteDatabase()`
    - `getRemoteDatabase()` always called `databaseStore.loadDatabases()`
    - this created knowledge-database unauthorized requests even on guest-accessible worldline pages
  - [WorldlineWorkbenchView.vue](D:/worldline/web/src/views/worldline/WorldlineWorkbenchView.vue)
    - `goToThemeChat()` called `buildAgentLocation()`
    - `buildAgentLocation()` called `ensureDefaultAgent()`
    - `ensureDefaultAgent()` called `agentStore.initialize()`
    - the login check happened after agent initialization, so guest users triggered agent unauthorized requests before being redirected to `/login`

## Implementation Judgment

- these two triggers are inside the allowed v1.2 patch surface
- they are public-shell noise, not required functionality for guest-mode worldline browsing
- they should be fixed in frontend only
- no backend patch is justified in this round because the observed noise is not caused by `system` public auth boundaries

## Actual Changes

- [AppLayout.vue](D:/worldline/web/src/layouts/AppLayout.vue)
  - `getRemoteDatabase()` now returns early when `userStore.isLoggedIn` is false
  - this stops guest-mode worldline routes from loading accessible databases through the shared shell
- [WorldlineWorkbenchView.vue](D:/worldline/web/src/views/worldline/WorldlineWorkbenchView.vue)
  - `goToThemeChat()` now checks guest state before calling `buildAgentLocation()`
  - guest mode still preserves theme-context redirect intent, but no longer initializes the agent store before redirecting to `/login`

## Validation

- build validation:
  - `cd D:/worldline/web && npm run build`
  - passed after the frontend patch
- real-backend smoke:
  - could not be fully completed in this round
  - local Docker daemon had to be restarted during validation
  - after restart, `api-dev` failed to expose stable `system` endpoints because backend startup hit an import-time Neo4j dependency path
  - latest observed blocker from `api-dev` logs:
    - `neo4j.exceptions.ServiceUnavailable`
    - import chain through `server/main.py -> server/routers -> src/knowledge -> UploadGraphService()`
    - as a result, `/api/system/health` could not be re-verified in the restarted environment

## Scope Judgment

- the new backend blocker is real, but it is outside the allowed scope of this round
- this round was limited to guest-shell noise reduction on public worldline routes
- fixing import-time graph coupling belongs to a separate backend/runtime stabilization pass

## Phase Judgment

- current phase: `v1.2 guest-shell noise reduction`
- readiness for next phase: `partially ready`
- main remaining gap before advancing:
  - re-run real Docker smoke in a stable backend environment
  - or run a dedicated backend stabilization pass to prevent `system` public endpoints from being blocked by graph startup coupling
