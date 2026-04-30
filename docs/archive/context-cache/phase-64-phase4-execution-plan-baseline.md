# Phase 64 - Phase 4b M1 baseline freeze implemented

## Baseline

- Start baseline:
  - Phase 61 confirmed `4b` start gate green
  - Phase 63 confirmed `4b-P0` readonly QA matrix and freeze condition
- This pass goal:
  - implement `M1 / 4b-P0` only
  - keep change scope inside auth boundary, route guard evidence, and baseline documentation
  - avoid graph feature expansion and avoid module-layer drift

## Subagent decomposition (actually executed)

1. `backend_worker`
   - reviewed backend runtime scope
   - determined no backend runtime code change was required
   - tightened auth-boundary coverage in graph API tests
2. `frontend_worker`
   - reviewed `/graph` route guard and fallback behavior
   - determined no frontend runtime code change was required
   - confirmed ordinary user fallback already lands on `/agent` route family
3. `qa_release_auditor`
   - normalized readonly QA packaging
   - landed M1 evidence package structure and docs/script updates
4. `system_mapper`
   - confirmed the pass stayed within `4b-P0` minimal scope
   - kept regression boundary limited to auth statuses and `/graph` fallback
5. `product_architect`
   - confirmed no PoE-specific assumption leaked into platform fixed layer
   - flagged only one residual risk: UI guard evidence must use fresh Playwright capture, not inherited placeholders

## Landed changes

### Runtime code

- No backend runtime files changed:
  - `server/utils/auth_middleware.py`
  - `server/routers/graph_router.py`
  - `server/main.py`
  - `server/routers/__init__.py`
- No frontend runtime files changed:
  - `web/src/router/index.js`
  - `web/src/apis/base.js`
  - `web/src/apis/graph_api.js`
  - `web/src/stores/user.js`
  - `web/src/views/GraphView.vue`
  - `web/src/layouts/AppLayout.vue`

### Tests and QA contract

1. `test/api/test_graph_router_list.py`
   - locked admin positive and standard-user negative assertions for graph list access

2. `test/api/test_unified_graph_router.py`
   - locked graph route auth requirements
   - locked standard-user negative access expectations
   - locked admin requirement for neo4j info endpoint

3. `scripts/qa_graph_auth_readonly_check.py`
   - normalized M1 evidence package output contract
   - kept checks readonly
   - aligned output names with `qa-phase4-m1-baseline-*`

4. `docs/21-readonly-qa-graph-auth-script.md`
   - updated readonly QA usage and evidence package guidance

5. `artifacts/qa-phase4-m1-baseline-20260403-074449/*`
   - refreshed tracked UI evidence files with a fresh Playwright capture
   - replaced inherited placeholder summary with current-session summary

6. `docs/context-cache/phase-64-phase4-execution-plan-baseline.md`
   - recorded the implemented M1 baseline and validation outcome

## Evidence package decision

- Authoritative M1 package:
  - `artifacts/qa-phase4-m1-baseline-20260403-074449/`
- Why this package is authoritative:
  - contains runtime probe
  - contains API matrix
  - now contains fresh `2026-04-03` UI evidence for standard-user `/graph` fallback

## Validation executed

1. Runtime gate
   - `docker compose ps`
   - `docker inspect --format "{{.State.Health.Status}}" graph`
   - `GET http://127.0.0.1:5050/api/system/health`
   - result: pass

2. Readonly QA self-check
   - `python scripts/qa_graph_auth_readonly_check.py --self-check`
   - result: pass

3. Scoped M1 auth-boundary replay
   - readonly QA package replay against local runtime
   - result: pass for anonymous `401`, user `403`, admin `200`

4. Scoped pytest replay
   - `python -m pytest test/api/test_graph_router_list.py::test_admin_can_list_graphs test/api/test_graph_router_list.py::test_standard_user_cannot_list_graphs test/api/test_unified_graph_router.py::test_graph_routes_require_auth test/api/test_unified_graph_router.py::test_standard_user_cannot_access_graph_endpoints test/api/test_unified_graph_router.py::test_get_neo4j_info_requires_admin -q`
   - result: `5 passed`

5. Playwright L2 replay
   - login as a standard user with `redirect=/graph`
   - final URL observed: `/agent/ChatbotAgent`
   - no `/api/graph/*` request observed during redirect flow
   - result: pass

## Scope boundary and residual risk

- M1 is green for the scoped contract only:
  - anonymous graph APIs blocked
  - ordinary user graph APIs blocked
  - admin graph APIs allowed
  - ordinary user `/graph` navigation fails closed to `/agent` route family
- Broader graph semantics are not re-certified by this pass.
- Existing broader graph tests still contain legacy failures outside `4b-P0` auth-boundary scope, so M1 should not be misreported as a full graph functional signoff.

## Phase judgment

- Current phase: `Phase 4b M1 baseline freeze landed`
- Readiness for next phase: `ready for M2 process hardening`
- Main remaining gap before advancing:
  - unify one replayable execution path for shell + API + Playwright evidence without relying on manual stitching
