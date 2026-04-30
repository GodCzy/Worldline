# Phase 77 - Phase 5 Shared View Semantic Decoupling And Docs Archive Tightening

## Summary

Phase 5 round 4 focused on two constrained targets:

1. Remove remaining PoE-specific content semantics from shared-facing pages without expanding functionality.
2. Tighten the docs main entry so historical numbered docs stay archived instead of occupying the active navigation surface.

This round did not change routes, permissions, or business capabilities.

## Subagent Decomposition

Read-only wave actually used:

1. `system_mapper`
   - scanned `ThemeDetailView.vue`, `AgentView.vue`, `GraphView.vue`
   - classified remaining PoE-specific content semantics into:
     - must change now in shared pages
     - allowed to stay inside module adapter

2. `product_architect`
   - fixed the boundary rule:
     - shared pages read module data through `@/data/worldline`
     - module-specific raw structures stay inside adapter
     - archive docs remain visible but leave the primary nav

3. `qa_release_auditor`
   - defined the minimum validation matrix:
     - `pnpm --dir web build`
     - `npm --prefix . run docs:build`
     - preview `/agent`, `/graph`, `/themes`

Implementation wave used:

4. `frontend_worker`
   - implementation guidance was used to remove the next must-change semantics from shared pages

5. `backend_worker`
   - explicitly confirmed no backend pairing change was required for this round

## Changes

### Frontend shared-page semantic decoupling

Changed files:

- `web/src/data/worldline/index.js`
- `web/src/data/worldline/poeWorldlineAdapter.js`
- `web/src/views/AgentView.vue`
- `web/src/views/themes/ThemeDetailView.vue`

Stable outcome:

- `AgentView.vue` no longer assembles shared-page context cards from PoE raw fields directly.
- `ThemeDetailView.vue` no longer uses `isPoeTheme` or page-local PoE raw field logic to render showcase sections.
- Shared-facing showcase data now comes from adapter-provided facade methods:
  - `getThemeShowcaseMeta`
  - `getThemeShowcaseCandidates`
  - `getThemeShowcaseGraphs`
  - `getAgentContextView`
- The only remaining direct `@/data/poePhase1` import stays in `web/src/data/worldline/poeWorldlineAdapter.js`, which is still an allowed module boundary.

### Docs archive tightening

Changed files:

- `docs/.vitepress/config.mts`
- `docs/archive/index.md`

Stable outcome:

- primary sidebar no longer exposes Phase 4 numbered docs directly
- the archive now owns the numbered historical docs and points users back to the current Phase 5 docs surface
- `docs/context-cache/**` remains excluded from VitePress build input

## Validation

Validated successfully:

```powershell
pnpm --dir D:\worldline\web build
npm --prefix D:\worldline run docs:build
```

Preview route checks passed:

```powershell
http://127.0.0.1:4173/agent  -> 200
http://127.0.0.1:4173/graph  -> 200
http://127.0.0.1:4173/themes -> 200
```

Additional checks:

- page-layer direct `@/data/poePhase1` imports remain cleared
- only `web/src/data/worldline/poeWorldlineAdapter.js` still imports `@/data/poePhase1`
- no backend route or auth contract changed in this round

## Remaining Risk

This round did not normalize historical mojibake-style Chinese copy already present in some shared Vue files.
That is now a content-quality / UX cleanup item, not an architecture blocker.

Also still not addressed in this round:

- large frontend bundle warnings
- repo-side historical artifact noise outside tracked files

## Phase Judgment

- current phase: `Phase 5 / shared-page semantic cleanup and docs archive tightening`
- readiness for next phase: `not ready to exit Phase 5 yet`
- main remaining gap before advancing:
  - normalize shared-page legacy copy quality
  - finish final repo/docs hygiene pass
