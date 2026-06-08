# Design

## 后端契约

现有 `WorldlineAgentWorkflowService` 已经在 run inspector 中支持 `audit_db_id`，并通过 `audit_tool_call()` 写 `worldline_mcp_audit_logs`。本阶段不扩大实现面，只补一个 focused test，验证当前行为是真实写表而不是响应字段伪装。

测试使用 SQLite `pg_manager` fixture，并插入最小 `KnowledgeBase` 作为审计日志外键目标。

## 前端 seed

`web/src/data/worldline/agentWorkbench.js` 仍有 Stage 1 文案，容易误导后续 Agent 判断 `/api/worldline/runs` 尚未实现。本阶段只更新描述，不改交互结构：

- 仍保留本地 preview seed。
- 明确后端 API 已可保存/读取。
- 后端不可用时仍可本地预览。

## 验证

- 运行新 focused pytest。
- 运行 `git diff --check` 覆盖本阶段文件。
- 若旧大测试仍 collection 超时，记录为既有验证限制，不用它证明本阶段。
