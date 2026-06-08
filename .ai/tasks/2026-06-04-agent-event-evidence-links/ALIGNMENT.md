# Agent Event Evidence Links Alignment

更新时间：2026-06-04

## 目标

把 Agent 工作台的 run ledger 事件从普通日志升级为 Evidence-backed 事件：事件条目可以直接看到关联的 evidence、tool call 和 temporal fact 线索。

## 范围

- 后端 `WorldlineRunLedgerService` 生成事件时添加兼容 summary 字段。
- 覆盖 `run.created`、`branch.approved`、`branch.rejected`、`skill.proposed`。
- 前端 `RUN EVENTS` 卡片展示 Evidence / Tool / Timeline / Permission chips。
- 保持无后端、未登录和非管理员时的本地 preview 事件可用。

## 不做

- 不新增数据库表。
- 不修改 router path。
- 不改变现有知识库、wiki、graph、timeline、MCP contract。
- 不引入新前端依赖。

## 验收

- 服务测试覆盖事件 summary 中的 evidence/tool/timeline 字段。
- 前端事件卡片能展示对应 chips。
- 构建、后端 focused test、浏览器截图通过。
