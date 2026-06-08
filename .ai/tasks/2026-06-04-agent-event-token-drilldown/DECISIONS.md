# Agent Event Token Drilldown Decisions

更新时间：2026-06-04

## 决策

- 先做同页 drilldown，不做跨页面路由。原因：当前工作台已有 Evidence Rail、Tool Trace、Timeline 和 Skill Genome，先把它们串成一个可操作闭环。
- Permission token 按权限字符串高亮同权限工具调用。原因：permission 不是独立实体 ID，不能假装可以定位到唯一对象。
- 后端 ledger 中找不到本地目标的 token 保持 disabled。原因：真实事件数据可能比本地 preview 更宽，前端不能制造不存在的实体详情。
