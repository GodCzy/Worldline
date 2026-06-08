# Agent Focus Dossier Design

更新时间：2026-06-04

## 设计

- `inspectorFocus` 继续作为唯一聚焦状态源。
- 新增 `focusedDossier` computed，根据 `inspectorFocus.type` 从现有数据中构建显示模型。
- Dossier 模型字段：
  - `type`
  - `title`
  - `badge`
  - `summary`
  - `meta`
  - `items`
- 事件详情 token 点击后先更新 `inspectorFocus`，再滚动到目标；Dossier 随同一状态自动刷新。

## 数据映射

- Evidence：`worldlineStore.evidenceRefs`，补充关联 entity 和 temporal fact。
- Tool：`agentRun.toolTraces`。
- Permission：同权限 `toolTraces` 聚合。
- Timeline：`worldlineStore.timelineRefs`，补充 evidence anchor。
- Skill：`agentRun.skillProposals`。

## 风险

- 真实后端 ledger 事件只返回 ID 时，如果当前页面没有目标对象，仍不会生成 Dossier。
- Evidence Dossier 只展示 metadata，不做文件内容读取。
- Permission Dossier 不是权限系统的完整授权视图，只是当前 run 中工具调用的权限聚合。
