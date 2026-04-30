# 前端结构

## Phase 5 重心

Phase 5 前端重构的核心不是改视觉，而是收回平台层边界。

当前的标准路径是：

- `themes/*`：模块选择和主题入口
- `worldline/*`：世界线生成与分支工作台
- `agent`：带上下文进入对话
- `graph`：带上下文进入知识图谱

## 共享视图规则

共享视图不能直接读取模块内部数据文件。  
它们应通过 worldline facade 获取：

- 展示标签
- graph loop
- 推荐候选
- graph 默认关键词

这样做的目的不是抽象而抽象，而是确保未来新增模块时，不需要回头修改共享视图去适配每个模块的私有结构。

## 现有骨架

- `WorldlineHubView`：模块选择和入口问题
- `WorldlineWorkbenchView`：世界线分支生成与 handoff
- `themeContextStore`：跨 `/worldline`、`/agent`、`/graph` 的共享上下文
- `worldlineContextStore`：当前世界线会话状态

## Phase 5 完成后的要求

1. `AgentView` 不再直接 import `@/data/poePhase1`
2. `GraphView` 不再直接 import `@/data/poePhase1`
3. 共享视图依赖平台 facade，模块能力由 adapter 提供
4. `/graph` 的权限守卫与回退语义保持 Phase 4 基线不变
