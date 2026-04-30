# Phase 49 - v1.2 public config singleflight signoff

## Baseline

- Prior baseline: `8306b75 chore(worldline): add shell playwright smoke path`
- Current focus: finish `v1.2` acceptance by resolving the only remaining public-route blocker on `/worldline`
- Existing state before this pass:
  - `/worldline/poe` passed minimum smoke
  - `/worldline/unknown` passed fail-closed smoke
  - shell Playwright screenshot workflow was available
  - MCP Playwright remained unstable and could not be treated as a blocking verification dependency

## First-wave subagent conclusions

### system_mapper

- Re-reviewed the 8-branch readability state after the density patch
- Judged the main stage as materially improved and usable
- Remaining issues were limited to minor tooltip direction and dense-label readability, not release blockers

### product_architect

- Produced the minimum Phase 3 config split:
  - platform-fixed items: layout mode, node hierarchy, edge density ceilings, hover capacity, fail-closed behavior
  - theme-configurable items: display copy, accent tokens, label dictionaries, branch archetype semantics
- Explicitly judged that themes must not override platform layout semantics or fallback behavior

### qa_release_auditor

- Initial verdict before implementation: `FAIL`
- Unique blocker:
  - `/worldline` public hub still had a public-config loading failure signature around `loadInfoConfig()`
- After the controller applied the minimal store-side patch and refreshed verification evidence:
  - Updated verdict: `PASS`
  - v1.2 can be formally closed

## Implementation pass

Only one runtime file was changed:

- `web/src/stores/info.js`

### What changed

- Added in-flight deduplication for public config loading
- `loadInfoConfig()` now reuses the same pending Promise during concurrent calls
- `reloadInfoConfig()` reuses the same request gate as well
- No API contract changes
- No routing changes
- No backend changes
- No theme-level behavior changes

### Why this was the minimum correct fix

The public config chain was being triggered from multiple entry points such as bootstrap, shared layout, and public views. The unsafe part was not the existence of multiple callers, but the lack of store-level singleflight protection. Fixing the store closed the concurrency hole without broad call-site cleanup.

## Validation

### Runtime / build checks

- `npm run build` passed
- `GET http://127.0.0.1:5173/api/system/health` returned `200`

### Browser smoke evidence

- shell Playwright artifacts were refreshed after the fix
- Refreshed evidence includes:
  - desktop `/worldline`
  - desktop `/worldline/poe`
  - desktop `/worldline/unknown`
  - fresh-profile `/worldline`

### Tooling note

- MCP Playwright remained unavailable in this session with `Target page, context or browser has been closed`
- This was treated as a tooling limitation, not a product blocker

## Phase judgment

- Current phase: `v1.2 acceptance closure`
- Readiness for next phase: `ready`
- Main remaining gap before advancing:
  - not a release blocker anymore
  - only a low-risk evidence completeness gap remains if we want a richer console-level trace or an explicit post-fix mobile `/worldline` capture

## Recommended next phase

Move into Phase 3 with focus on:

1. visual configuration formalization
2. theme-boundary hardening
3. remaining line-tree polish for dense branch scenes
