# Agent Workbench Ledger Sync Design

更新时间：2026-06-04

## 前端状态

新增本地状态：

- `ledgerRunId`：后端持久化 run id。
- `ledgerEvents`：事件列表。
- `ledgerBusy`：保存、审批、刷新或提交技能时的忙状态。
- `ledgerMessage`：给用户展示的当前连接/权限/失败提示。
- `ledgerError`：保留最近一次错误文本。

## 数据合并

后端 Stage 2 ledger 返回的是标准 run payload，但本地 Agent 工作台还有 `toolTraces`、`gateResults`、`contract`、`displayMeta` 等 UI 专用字段。前端合并时：

- 后端字段优先更新 `id/status/branches/episodes/skillProposals/events`。
- 本地 UI 字段继续保留。
- 合并后的 payload 继续传入 `worldlineStore.hydrate`。

## 权限

`/api/worldline/runs` 受 admin 保护。前端根据 `useUserStore().isAdmin` 控制动作：

- 非管理员：保留本地预览，禁用后端写操作。
- 管理员：允许保存、审批、提交技能和刷新事件。

## 失败策略

API 调用失败时不清空当前世界线，只显示失败信息并保留本地预览，避免因为后端暂不可用导致首页或工作台不可用。
