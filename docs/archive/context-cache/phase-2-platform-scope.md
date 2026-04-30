# 世界线 Phase 2 Platform Scope

## 当前目标

在不侵入 RAG、知识图谱和 Agent 核心编排层的前提下，完成“世界线”平台层第一批最小改造方案收敛。

本阶段只定义和准备平台层改造面：

- 首页
- 路由
- 导航
- 模块入口
- 平台上下文的最小透传方式

不进入：

- PoE 知识导入
- PoE 问答模板接线
- 图谱实体落库
- 推荐逻辑实现

## repo_mapper 复核结果

### 前端入口与平台入口

- 前端启动入口：`web/src/main.js`
- 路由入口：`web/src/router/index.js`
- 平台主布局：`web/src/layouts/AppLayout.vue`
- 公共首页：`web/src/views/HomeView.vue`
- 用户菜单入口：`web/src/components/UserInfoComponent.vue`
- 品牌配置读取：`web/src/stores/info.js`

### 后台入口

- 后台导航入口在 `web/src/layouts/AppLayout.vue`
- 后台页面主入口当前包括：
  - `web/src/views/DashboardView.vue`
  - `web/src/views/DataBaseView.vue`
  - `web/src/views/DataBaseInfoView.vue`
  - `web/src/views/GraphView.vue`
  - `web/src/views/ExtensionsView.vue`

### 后端入口与可扩展入口

- HTTP 入口：`server/main.py`
- API 聚合入口：`server/routers/__init__.py`
- 品牌/公开信息配置入口：`server/routers/system_router.py` 的 `/api/system/info`

### 本阶段低风险可改文件

- `src/config/static/info.template.yaml`
- `web/src/stores/info.js`
- `web/src/router/index.js`
- `web/src/layouts/AppLayout.vue`
- `web/src/views/HomeView.vue`
- `web/src/components/UserInfoComponent.vue`

### 本阶段不建议触碰的高风险文件

- `src/knowledge/base.py`
- `src/knowledge/manager.py`
- `src/knowledge/implementations/lightrag.py`
- `src/agents/common/base.py`
- `src/agents/chatbot/graph.py`
- `src/services/chat_stream_service.py`
- `src/services/agent_run_service.py`
- `server/routers/chat_router.py`
- `server/routers/knowledge_router.py`
- `server/routers/graph_router.py`

## platform_architect 收敛结论

### 结论 1：第二阶段优先走“配置驱动 + 前端平台化”路径

当前 `/api/system/info` 已经能返回完整品牌配置，因此平台层第一批改造不需要先新增后端接口。

最稳妥路径是：

1. 在 `src/config/static/info.template.yaml` 中增加主题模块描述
2. 在 `web/src/stores/info.js` 中暴露 `themes/modules` 计算属性
3. 在前端首页、导航、路由中消费这些配置

### 结论 2：平台层上下文先在前端建立，不先侵入后端核心服务

本阶段只需要一个最小上下文对象即可：

```json
{
  "theme": "poe",
  "module": "poe",
  "scene": "overview",
  "version": "phase2"
}
```

第一轮先通过路由参数或路由 meta 建立前端上下文，不急着透传到聊天、知识库和图谱服务。

### 结论 3：第一批改动文件建议

- `src/config/static/info.template.yaml`
  - 增加世界线主题模块清单，例如 `themes` 或 `modules`
- `web/src/stores/info.js`
  - 增加 `themes/modules` 计算属性
- `web/src/router/index.js`
  - 新增平台模块入口路由，例如 `/themes/poe`
- `web/src/views/HomeView.vue`
  - 首页改造成“平台首页 + 首期主题入口”
- `web/src/layouts/AppLayout.vue`
  - 导航增加平台视角入口或模块入口承载区
- `web/src/components/UserInfoComponent.vue`
  - 去掉上游文档硬编码，改为读取世界线文档地址
- 可新增文件：
  - `web/src/views/themes/ThemeHubView.vue`
  - `web/src/views/themes/PoeThemeView.vue`
  - `web/src/stores/themeContext.js`

### 结论 4：后台保持原样，平台入口先覆盖公共首页与主题入口

后台现有 Dashboard、知识库、图谱、扩展管理先保留原结构。

世界线平台化第一批重点不是重做后台，而是：

- 给平台建立统一身份
- 给 PoE 建立独立主题入口
- 给后续模块扩展预留稳定路径

## poe_designer 对平台层的最小约束

平台层至少要支持一个可配置主题卡片，字段建议包括：

- `id`
- `name`
- `subtitle`
- `description`
- `status`
- `entry_route`
- `tags`

PoE 第一批平台入口只需要支持：

- 主题简介
- 演示定位
- 后续可接入知识库/问答/图谱的入口占位

## 建议实施顺序

1. 先补平台模块配置结构
2. 再补信息 store 的主题读取能力
3. 再补首页主题入口
4. 再补路由与主题页面骨架
5. 最后补导航和用户菜单中的世界线平台链接

## 下一步

如果进入实现阶段，优先由 `implementer` 做“前端平台层最小改造”，暂不新增后端业务接口。
