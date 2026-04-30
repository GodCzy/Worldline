# Phase 74 - Phase 5 platform decoupling and docs reset baseline

## Stable conclusions

- Phase 5 has started as a real refactor phase, not as an extension of Phase 4 acceptance work.
- Shared platform views no longer import `@/data/poePhase1` directly:
  - `web/src/views/AgentView.vue`
  - `web/src/views/GraphView.vue`
- Worldline adapter registry now exposes shared-view-safe facade methods through:
  - `web/src/data/worldline/index.js`
  - `web/src/data/worldline/poeWorldlineAdapter.js`
- Docs site has been reset from legacy phase-centric navigation to current product-centric navigation:
  - home
  - platform architecture
  - frontend architecture
  - backend architecture
  - module extension
  - operations and validation
  - archive
- `docs/context-cache/` remains a repo-side audit area and is excluded from VitePress build input.
- Backend router/bootstrap structure has been tightened without changing public API paths or Phase 4 auth/graph contracts.

## Validation executed

- `pnpm --dir web build` -> pass
- `npm run docs:build` -> pass
- `python -m py_compile server/main.py server/routers/__init__.py server/routers/graph_router.py server/routers/system_router.py` -> pass
- `python scripts/qa_graph_auth_readonly_check.py --self-check` -> pass
- `python scripts/qa_phase4_m2_replay.py --help` -> pass

## Explicitly not completed in this pass

- Live API integration tests in `test/api/test_graph_router_list.py` and `test/api/test_unified_graph_router.py` were attempted conceptually, but local execution remains blocked by missing `TEST_USERNAME` / `TEST_PASSWORD` environment variables.
- Broader PoE-specific coupling outside shared platform views still exists in module-specific pages such as theme detail surfaces; that is follow-up work, not a blocker for this baseline.

## Phase judgment

- Current phase: `Phase 5 / platform decoupling and docs reset`
- Readiness for next phase: `not ready for next phase yet`
- Main remaining gap before advancing:
  - continue shrinking module-specific coupling outside shared views
  - complete live API regression with valid admin test credentials
