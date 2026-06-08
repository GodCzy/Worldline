# Agent Focus Dossier Decisions

更新时间：2026-06-04

## 决策

- Focus Dossier 放在 `EVENT DETAIL` 下方。原因：用户从事件 token 出发，需要在同一上下文内看到目标解释，而不是跳出当前事件。
- 先用当前 payload 元数据构建 Dossier。原因：本阶段目标是强化 Agent 工作台可审查闭环，不改变后端数据契约。
- Permission Dossier 以同权限工具调用聚合呈现。原因：permission 字符串不是唯一实体，不能假装有单一目标对象。
