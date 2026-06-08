# Agent Event Detail Inspector Design

更新时间：2026-06-04

## 状态

- `selectedEventId`：当前选中的事件。
- `selectedLedgerEvent`：从过滤后的事件列表中解析选中事件，若当前选择不在过滤结果内，则回退到当前过滤列表第一条。

## 交互

- 点击事件卡片：
  - 设置 `selectedEventId`。
  - 若事件存在 `branchId`，同步 `worldlineStore.setSelectedNode(branchId)`。
- 过滤事件时，详情面板自动展示当前过滤结果中的第一条事件。

## 展示

详情面板包含：

- Meta：event type、actor、branch、run id。
- Summary：格式化后的事件摘要。
- Linked Evidence：`evidenceIds`。
- Tool Calls：`toolCallIds`。
- Timeline Facts：`temporalFactIds`。
- Permissions：`requiredPermissions`。
- Evidence Runs：`evidenceRunIds`。

## 风险

当前只是 ID 级明细，不做 EvidenceAnchor 或 MCP audit 详情查询；深跳转和详情抽屉留到下一阶段。
