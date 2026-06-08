# Alignment

## Goal

Expose run replay artifacts through the controlled `worldline` MCP boundary so external Agents can inspect saved replay exports without direct file or database access.

## Scope

- Add a read-only manifest tool: `worldline.inspect_run_artifacts`.
- Implement a service method that reads artifacts from `WorldlineRunLedgerService`.
- Expose the method in `src/mcp/worldline_server.py`.
- Record an MCP audit summary for artifact inspection through `WorldlineAgentWorkflowService`.
- Add focused tests for manifest, service behavior, and server wiring.

## Out Of Scope

- No direct database-write MCP.
- No unrestricted filesystem MCP.
- No artifact mutation through MCP.
- No new storage schema or migration.
- No frontend UI change in this stage.

## Acceptance

- Manifest includes the read-only artifact inspection tool with `write_scope: none`.
- Service returns artifact list and optional content preview.
- MCP server exposes `worldline_inspect_run_artifacts`.
- Focused tests pass.
- Evidence and OutputMD summary are written.
