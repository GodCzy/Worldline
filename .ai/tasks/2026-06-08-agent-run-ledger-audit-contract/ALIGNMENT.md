# Alignment

日期：2026-06-08

## 目标

推进 P1「Agent 工作台与 Run Ledger 真实后端联通」中最小高价值缺口：证明 run inspector 的 MCP 读契约在传入 `audit_db_id` 时会写入 `worldline_mcp_audit_logs`，并清理前端本地 seed 中把持久化账本描述为 future work 的过期文案。

## 验收

- `worldline.inspect_run_manifest`、`worldline.inspect_run_artifacts`、`worldline.inspect_run_gates`、`worldline.inspect_run_evidence`、`worldline.inspect_run_knowledge` 在有 `audit_db_id` 时记录审计日志。
- not found 的 run resource 读取也记录审计状态，而不是静默失败。
- focused pytest 不依赖旧的宽集成测试文件 collection。
- Agent Workbench 文案明确 `/api/worldline/runs` 已存在，仍保留后端不可用时的本地预览 fallback。

## 边界

- 不改变 file-backed ledger 存储策略，不新增数据库 schema。
- 不回滚未知脏工作树。
- 不把临时 token、密码或本地凭据写入文件。
