# MCP suggested steps (manual)

This script only runs read-only API checks. Use MCP Playwright to verify UI guard behavior:
1. Open `http://127.0.0.1:5173/login` and sign in with a QA account that has `role=user`.
2. Navigate directly to `http://127.0.0.1:5173/graph`.
3. Expected: frontend guard redirects to `/agent` or `/agent/{agent_id}`.
4. In Network panel, filter `api/graph` and confirm no successful admin-only graph access.
5. If unexpected behavior appears (for example `role=user` gets `200`), capture URL, status code, and response summary.

Key backend URLs:
- http://127.0.0.1:5050/api/auth/me
- http://127.0.0.1:5050/api/graph/list
- http://127.0.0.1:5050/api/graph/neo4j/info
