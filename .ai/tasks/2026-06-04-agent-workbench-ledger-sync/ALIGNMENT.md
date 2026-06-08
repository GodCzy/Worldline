# Agent Workbench Ledger Sync Alignment

更新时间：2026-06-04

## 目标

把 `/worldline/agent` 从纯本地预览推进到可连接 Stage 2 run ledger API 的前端工作台。

## 范围

- 使用现有 `worldlineRunApi`：
  - `POST /api/worldline/runs`
  - `GET /api/worldline/runs/{run_id}/events`
  - `POST /api/worldline/runs/{run_id}/branches/{branch_id}/approve`
  - `POST /api/worldline/runs/{run_id}/skills/propose`
- 保留后端不可用、未登录或非管理员时的本地预览能力。
- 保持 payload 可被 `worldlineStore.hydrate` 消费。

## 不做

- 不新增数据库表或迁移。
- 不改变现有知识库、图谱、wiki、timeline 或 MCP API contract。
- 不引入新前端依赖。

## 验收

- 页面显示当前账本状态、事件数和管理员能力提示。
- 管理员可保存当前 run 到后端账本。
- 分支 Inspector 的批准动作可调用后端审批。
- Skill Genome 候选可提交到后端。
- 构建通过，浏览器截图无明显布局断裂。
