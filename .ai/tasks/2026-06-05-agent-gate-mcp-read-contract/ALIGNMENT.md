# Worldline Agent Gate MCP Read Contract - Alignment

## Goal

把 Agent Workbench 中已有的 gate result 从纯前端可见状态升级为受控 MCP 只读对象：外部 Agent 可以通过 `worldline.inspect_run_gates` 读取 run ledger 中的 gate results，前端 Gate panel 和 Focus Dossier 可以复制对应 MCP read call。

## Scope

- 新增后端只读 service 方法，不改变 run ledger 存储 schema。
- 新增 MCP tool `worldline.inspect_run_gates`。
- 更新 manifest 和 focused tests。
- 前端新增 gate MCP call 预览与 `Copy MCP` 快捷入口。
- 不引入数据库写 MCP，不绕过 Worldline service boundary。

## Acceptance

- `WorldlineAgentWorkflowService.tool_manifest()` 包含 `worldline.inspect_run_gates`，`write_scope` 为 `none`。
- `WorldlineAgentWorkflowService.inspect_run_gates()` 能按 run 或 gate_id 读取 gate result。
- MCP server 暴露 `worldline_inspect_run_gates`。
- 前端 Gate Run 和 Focus Dossier gate link 都能复制 gate MCP read call，并显示 Last MCP Call。
- 后端 focused pytest、前端 build、浏览器 QA 通过或记录阻塞。
