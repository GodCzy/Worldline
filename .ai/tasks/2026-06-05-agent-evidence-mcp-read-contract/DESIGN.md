# Design

## Backend

`WorldlineRunLedgerService`:

- `_normalize_run` 保存 `evidenceRefs`。
- `_normalize_evidence_ref` 标准化 EvidenceAnchor 相关字段。
- `list_evidence(run_id, limit, offset)` 返回 `run_id`, `items`, `total`, `limit`, `offset`。

`WorldlineAgentWorkflowService`:

- `inspect_run_evidence(run_id, evidence_id, source_id, limit, audit_db_id, actor)`。
- URI:
  - Evidence: `worldline-run-ledger://<run_id>/evidence/<evidence_id>`
  - Source: `worldline-run-ledger://<run_id>/sources/<source_id>`
- View includes EvidenceAnchor, SourceAsset, and DocumentNode metadata already present in frontend fixtures.

## MCP

Tool:

- `worldline.inspect_run_evidence`
- `write_scope: none`
- `dispatch_backend: inline`
- Args: `run_id`, optional `evidence_id`, optional `source_id`, `limit`, `audit_db_id`

## Frontend

Add MCP call builder for evidence/source:

- Tool: `worldline.inspect_run_evidence`
- Evidence args: `run_id`, `evidence_id`, `audit_db_id`
- Source args: `run_id`, `source_id`, `audit_db_id`

Focus Dossier links for `evidence` and `source` get `Copy MCP`, and local preview displays URI/Args.
