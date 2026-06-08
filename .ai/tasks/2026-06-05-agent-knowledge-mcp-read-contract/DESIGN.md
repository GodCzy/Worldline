# Design

## Backend

`WorldlineRunLedgerService`:

- `_normalize_run` stores top-level `wikiRefs`, `entityRefs`, `timelineRefs`.
- If top-level refs are absent, flatten compatible branch refs.
- `list_knowledge(run_id, kind, limit, offset)` returns run-scoped knowledge references.

`WorldlineAgentWorkflowService`:

- `inspect_run_knowledge(run_id, kind, item_id, limit, audit_db_id, actor)`.
- `kind` accepts `wiki`, `graph`, `timeline`, or `all`.
- URI shapes:
  - `worldline-run-ledger://<run_id>/wiki/<wiki_id>`
  - `worldline-run-ledger://<run_id>/graph/<entity_id>`
  - `worldline-run-ledger://<run_id>/timeline/<fact_id>`

## MCP

Tool:

- `worldline.inspect_run_knowledge`
- `write_scope: none`
- `dispatch_backend: inline`
- Args: `run_id`, optional `kind`, optional `item_id`, optional `limit`, optional `audit_db_id`

## Frontend

- Add a knowledge MCP call builder and copier.
- `Wiki`, `Graph`, and `Time` Focus Dossier links get `Copy MCP`.
- Last MCP Call and Focus Dossier MCP Preview reuse the existing generic preview surface.

## Validation

- Focused pytest for ledger list API and MCP service selection.
- Manifest test update.
- Vite build.
- Browser QA by Chrome CDP on `/worldline/agent`.
