# Design

## Backend

`WorldlineAgentWorkflowService.inspect_run_manifest(run_id, include_resources, limit, audit_db_id, actor)`:

- Loads run from `WorldlineRunLedgerService`.
- Reuses existing run read views:
  - artifacts -> `worldline.inspect_run_artifacts`
  - gates -> `worldline.inspect_run_gates`
  - evidence -> `worldline.inspect_run_evidence`
  - sources -> `worldline.inspect_run_evidence`
  - wiki/graph/timeline -> `worldline.inspect_run_knowledge`
- Returns a manifest with:
  - `contractVersion`
  - `run`
  - `sections`
  - `resourceCounts`
  - `tools`
  - `storage`

## MCP

Tool:

- `worldline.inspect_run_manifest`
- `write_scope: none`
- `dispatch_backend: inline`
- Args: `run_id`, `include_resources`, `limit`, `audit_db_id`

## Frontend

Add Run MCP Manifest rail/card near the existing MCP Readable area:

- Shows current manifest state and resource counts.
- Copy button writes a tool call for `worldline.inspect_run_manifest`.
- Last MCP Call panel reuses existing display surface.

## Validation

- Focused backend tests for manifest contract and missing run.
- Manifest test update.
- Vite build.
- Chrome CDP browser QA with screenshot.
