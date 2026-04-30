# M1 Read-Only QA Evidence Summary

- package: `qa-phase4-m1-baseline-20260403-074449`
- contract: `phase4-m1`
- pass_count: 7
- fail_count: 0
- readonly: `yes`
- ui_capture: `fresh-playwright-2026-04-03`

## Checks
- [PASS] anonymous_health | GET http://127.0.0.1:5050/api/system/health | status=200 | expected=200
- [PASS] anonymous_graph_list | GET http://127.0.0.1:5050/api/graph/list | status=401 | expected=401
- [PASS] anonymous_graph_neo4j_info | GET http://127.0.0.1:5050/api/graph/neo4j/info | status=401 | expected=401
- [PASS] user_token_graph_list_negative | GET http://127.0.0.1:5050/api/graph/list | status=403 | expected=403
- [PASS] user_token_graph_neo4j_info_negative | GET http://127.0.0.1:5050/api/graph/neo4j/info | status=403 | expected=403
- [PASS] admin_token_graph_list_positive | GET http://127.0.0.1:5050/api/graph/list | status=200 | expected=200
- [PASS] admin_token_graph_neo4j_info_positive | GET http://127.0.0.1:5050/api/graph/neo4j/info | status=200 | expected=200

## Compatibility
- Legacy compatibility files remain available: `result.json`, `result.txt`, `run_config.json`, `mcp_next_steps.md`.
- This package is read-only and does not create, update, or delete business data.

## Runtime
- `10-runtime-health.txt`: runtime shell checks and probe summary

## UI
- `30-ui-graph-guard.png`: fresh 2026-04-03 Playwright screenshot after standard user login redirect
- `31-ui-network-graph-guard.txt`: fresh request summary; no `/api/graph/*` request observed in user redirect flow
- `32-ui-final-url-assertion.json`: fresh final URL assertion; pathname=`/agent/ChatbotAgent`, `isAllowedFallback=true`