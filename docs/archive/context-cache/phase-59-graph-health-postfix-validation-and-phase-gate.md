# Phase 59 - graph health postfix validation and phase gate

## Baseline

- Start head: `73b4c07` (Phase 4a shell style + redirect continuity completed)
- Main blocker from previous phase gate: `graph` service reported `unhealthy`

## Subagent decomposition (actually executed)

Read/diagnose wave:

1. `backend_worker` (`019d4935-a601-7bc3-bf7d-e4b80850931f`)
   - identified root cause: graph healthcheck used `curl` which is missing in `neo4j:5.26`
   - applied minimal fix in compose files and committed it
2. `system_mapper` (`019d4935-dd26-7293-a5f9-faedbf2f7a62`)
   - mapped dependency chain and minimal regression boundary for graph line
3. `qa_release_auditor` (`019d4935-c187-7433-abd8-c59b58fd8de8`)
   - produced shell+MCP acceptance matrix (pre-fix snapshot showed graph still unhealthy)

Controller postfix verification:

- reran health/status checks after fix commit
- reran MCP route evidence on `/worldline` and `/graph` redirect behavior

## Minimal fix landed

Commit: `00a0b61 fix(graph): use wget healthcheck for neo4j container`

Changed files in that fix:

- `docker-compose.yml`
- `docker-compose.prod.yml`
- `docs/context-cache/phase-58-graph-healthcheck-curl-missing-fix.md`

Core change:

- `graph.healthcheck.test` switched from `curl` to `wget -qO- ... >/dev/null`

## Post-fix validation (controller)

Shell validation:

- `docker compose ps graph` => `Up ... (healthy)`
- `docker inspect --format "{{.State.Health.Status}}" graph` => `healthy`
- endpoint checks:
  - `http://127.0.0.1:5050/api/system/health` -> `200`
  - `http://127.0.0.1:5173/worldline` -> `200`
  - `http://127.0.0.1:5173/worldline/poe` -> `200`
  - `http://127.0.0.1:5173/worldline/unknown` -> `200`
  - `http://127.0.0.1:5173/graph` -> `200` (frontend shell reachable)
  - `http://127.0.0.1:5050/api/graph/list` -> `401` (unauthenticated expected)
  - `http://127.0.0.1:5050/api/graph/neo4j/info` -> `401` (unauthenticated expected)

MCP Playwright validation:

- navigation + screenshot succeeded (no `Transport closed`)
- evidence:
  - `artifacts/qa-release-audit-20260401-postfix/phase4a-postfix-worldline.png`
  - `artifacts/qa-release-audit-20260401-postfix/phase4a-postfix-graph.png`
- `/graph` navigation redirected to `/login?redirect=/graph` as expected by auth guard

## Consolidated judgment

- `graph unhealthy` blocker: **closed**
- Playwright MCP transport stability: **green in current session**
- Phase gate to move beyond 4a: **conditionally ready**

Main remaining gap before broader 4b:

- authenticated admin-session end-to-end evidence for graph page + graph APIs (currently only unauthenticated guard path verified)
