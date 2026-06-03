# Phase 14 MCP And Agent Workflow Phase 6

Updated: 2026-06-03

## Implemented

- `WorldlineWorkflowRun`
- `WorldlineMcpAuditLog`
- `WorldlineAgentWorkflowService`
- `src.mcp.worldline_server`
- Built-in MCP candidate config for `worldline`
- Admin endpoints:
- `GET /knowledge/databases/{db_id}/worldline-mcp/manifest`
- `GET /knowledge/databases/{db_id}/worldline-mcp/audit-logs`
- `POST /knowledge/databases/{db_id}/worldline-workflows/plan`

## Tool Boundary

Worldline MCP tools are controlled tools:

- `worldline.compile_document`
- `worldline.rebuild_wiki`
- `worldline.update_graph`
- `worldline.run_quality_gate`
- `worldline.inspect_timeline`

Write tools require admin and route through service boundaries. External agents do not get direct DB writes.

Every controlled workflow/tool call can write an audit row with tool name, actor, status, request summary, result summary, and metadata.

## Runtime Contract

Workflow plans are LangGraph-shaped DAGs and include ARQ dispatch metadata. Real Redis/ARQ worker execution remains a later runtime-hardening step.
