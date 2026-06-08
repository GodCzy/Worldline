# Design

## Backend

新增 `WorldlineRunLedgerService.list_gates(run_id, limit, offset)`：

- 从 `run["gateResults"]` 读取 normalized gate result。
- 不修改 `runs.json` 结构。
- 返回分页结构：`run_id`, `items`, `total`, `limit`, `offset`。

新增 `WorldlineAgentWorkflowService.inspect_run_gates()`：

- 参数：`run_id`, `gate_id`, `limit`, `audit_db_id`, `actor`。
- 返回只读 view：id, runId, branchId, label, status, value, summary, threshold, input, failureReason, remediation, toolCallIds, artifactIds, uri。
- URI 使用 `worldline-run-ledger://<run_id>/gates/<gate_id>`。
- 可选 `audit_db_id` 时写入 MCP audit log。

## MCP

新增 tool：

- Python function: `worldline_inspect_run_gates`
- Manifest name: `worldline.inspect_run_gates`
- `write_scope: none`
- `dispatch_backend: inline`

## Frontend

在 Agent Workbench 新增 gate MCP call builder：

- Tool: `worldline.inspect_run_gates`
- URI: `worldline-run-ledger://<run_id>/gates/<gate_id>`
- Args: `run_id`, `gate_id`, `audit_db_id: ""`

Gate Run panel 和 Focus Dossier gate rows 增加 `Copy MCP`，并复用 Last MCP Call 预览区域。
