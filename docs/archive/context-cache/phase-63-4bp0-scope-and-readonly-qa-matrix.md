# Phase 63 - 4b P0 scope and unified readonly QA matrix baseline

## Baseline

- Start head: `d19d6ac`
- Prior gate status: 4b start gate already green (Phase 61)
- This pass goal:
  - define 4b-P0 target list + prohibited scope
  - unify admin positive + user negative acceptance matrix
  - land a reusable read-only QA script/doc entry (no business logic change)

## Subagent decomposition (actually executed)

1. `system_mapper`
   - produced 4b-P0 goals, prohibited scope, and freeze condition
2. `qa_release_auditor`
   - produced a single matrix combining admin positive and user negative evidence
   - provided replay sequence and evidence naming convention
3. `backend_worker`
   - added read-only QA script/doc entry only; no business logic modifications

## Landed deliverables

1. `scripts/qa_graph_auth_readonly_check.py`
   - read-only by default (GET-only checks)
   - validates graph/auth boundary status codes
   - writes run artifacts to `artifacts/qa-readonly-graph-auth-<timestamp>/`
   - emits MCP manual follow-up steps file

2. `docs/21-readonly-qa-graph-auth-script.md`
   - usage guide, safety boundary, output contract

3. `docs/context-cache/phase-62-readonly-qa-graph-auth-script-baseline.md`
   - script-baseline milestone and self-check note

## Validation executed

1. `python scripts/qa_graph_auth_readonly_check.py --self-check`
   - pass
2. `python scripts/qa_graph_auth_readonly_check.py --api-base http://127.0.0.1:5050 --frontend-base http://127.0.0.1:5173`
   - pass

## Consolidated 4b-P0 freeze condition

Freeze when all are continuously green:

- container: `api-dev` healthy, `graph` healthy
- anonymous: `/api/graph/list` and `/api/graph/neo4j/info` return `401`
- admin: both graph APIs return `200`, `/graph` can enter
- user: both graph APIs return `403`, `/graph` falls back to `/agent` or `/agent/{id}`

## Phase judgment

- Current phase: `Phase 4b P0 baseline setup`
- Readiness: `ready to freeze 4b runtime baseline`
- Main remaining gap before next expansion:
  - none at blocker level; next step is process hardening (single command smoke orchestration + CI wiring)
