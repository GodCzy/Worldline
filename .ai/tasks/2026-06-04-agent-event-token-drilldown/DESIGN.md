# Agent Event Token Drilldown Design

更新时间：2026-06-04

## 设计

- 事件详情 section 继续从 `event.summary` 的列表字段派生。
- 每个 token 在渲染前解析为 `targetType`、`targetId`、`layer`、`branchId` 和 `canFocus`。
- 点击 token 时：
  1. 如目标有关联分支，先调用 `selectBranch(branchId)`。
  2. 更新 `inspectorFocus` 状态。
  3. 需要 evidence/timeline 时通过 props 驱动 Evidence Rail 切 tab。
  4. 等待 DOM 更新后滚动到 `[data-inspector-target="type:id"]`。

## 目标映射

- `evidenceIds` -> Evidence Rail `evidence` tab。
- `temporalFactIds` -> Evidence Rail `timeline` tab + Timeline Scrubber temporal item。
- `toolCallIds` -> Tool Trace item。
- `requiredPermissions` -> Tool Trace permission group。
- `evidenceRunIds` -> 包含该 run id 的 Skill Proposal。

## 风险

- 后端 ledger 事件可能只返回 ID，页面当前没有对应实体时只能显示 disabled token。
- Permission 不是唯一 ID，点击后会高亮所有同权限工具调用。
- Evidence Run 当前在 preview 数据里只关联 Skill Proposal，不等价于完整运行回放详情。
