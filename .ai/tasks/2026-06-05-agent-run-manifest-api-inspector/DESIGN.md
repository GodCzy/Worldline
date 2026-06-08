# Design

## Backend

Add to `server/routers/worldline_run_router.py`:

- `GET /worldline/runs/{run_id}/manifest`
- Query params:
  - `include_resources: bool = true`
  - `limit: int = 50`
  - `audit_db_id: str | None = None`
- Admin-only via existing `get_admin_user`.
- Calls `WorldlineAgentWorkflowService.inspect_run_manifest`.
- Returns `404` only if the service manifest status is `not_found`; otherwise returns the service payload.

## Frontend API

Add to `web/src/apis/worldline_api.js`:

- `getWorldlineRunManifest(runId, params)`

This keeps the API call with the existing Worldline API module instead of embedding fetch logic inside the view.

## Frontend UI

Extend the Agent Workbench `Run MCP Manifest` area with an API inspector:

- Load button.
- Backend status line.
- Counts from backend manifest sections.
- Tool list.
- Sample resource URIs.
- Failure message when backend unavailable or run not found.

The existing copy button and Last MCP Call panel remain unchanged.

## Validation

- Focused pytest for run manifest route.
- Existing run ledger/MCP tests.
- Vite build.
- CDP browser QA against `http://127.0.0.1:5173/worldline/agent`.
