# Alignment

## Goal

Bridge the new run-level MCP manifest into the HTTP/API and Agent Workbench UI so the frontend can inspect backend-derived manifest sections, counts, tools, and read-only resources instead of only showing locally inferred copy instructions.

## Scope

- Add a read-only HTTP route for run manifest inspection.
- Reuse `WorldlineAgentWorkflowService.inspect_run_manifest` rather than duplicating manifest assembly.
- Add a frontend API helper for the manifest endpoint.
- Add an Agent Workbench manifest inspector that can load and display backend manifest counts/tools/resources for the active run.
- Preserve the existing copy-only `Run MCP Manifest` call path.

## Out Of Scope

- No new database schema.
- No new write MCP.
- No direct database-write MCP or unrestricted external Agent writes.
- No replacement of existing run ledger create/get/events/artifact routes.

## Acceptance

- Backend route exposes `GET /api/worldline/runs/{run_id}/manifest`.
- Route returns the same `worldline-run-mcp-manifest-v0.1` contract as MCP/service.
- Tests prove route behavior for existing and missing runs.
- Frontend can load backend manifest from the active run and display status, counts, tools, and sample resources.
- Browser QA proves the inspector loads and renders a backend manifest snapshot.
