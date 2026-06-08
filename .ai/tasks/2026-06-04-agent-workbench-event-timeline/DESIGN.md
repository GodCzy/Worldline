# Agent Workbench Event Timeline Design

更新时间：2026-06-04

## 事件来源

1. `ledgerEvents`：后端 run ledger API 返回的真实事件。
2. `previewLedgerEvents`：当前本地 run 派生出的预览事件。

真实事件优先；没有真实事件时展示预览事件，并标注 `preview`。

## 过滤

事件按 `eventType` 前缀归类：

- `run.*`
- `branch.*`
- `tool.*`
- `skill.*`

未知类型保留在 `all` 中。

## 分支联动

如果事件有 `branchId`，点击事件卡片时调用 `selectBranch(branchId)`，同步画布和 Branch Inspector 焦点。

## 文案策略

后端 `summary` 是对象，前端把关键字段格式化成短句，避免直接展示 JSON。
