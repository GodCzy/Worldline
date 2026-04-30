# 世界线 Phase 2 Platform Implementation

## 本轮目标

完成“平台层最小实现”，仅做配置驱动的前端平台化：

- 新增主题分区入口
- 新增 PoE 主题页面骨架
- 让首页、导航、用户菜单与登录页统一到世界线平台入口

## 已完成实现

### 配置层

- `src/config/static/info.template.yaml`
  - 新增 `branding.description`
  - 新增 `themes` 配置
  - 为 `poe` 定义 `entry_route`、`tags`、`highlights`、`context`、`links`、`entry_points`

### 平台数据读取层

- `web/src/stores/info.js`
  - 新增 `themes`
  - 新增 `primaryTheme`
  - 新增 `docsUrl`
  - 新增 `projectRepoUrl`
  - 新增 `getThemeById`

### 路由层

- `web/src/router/index.js`
  - 新增 `/themes`
  - 新增 `/themes/:themeId`
  - 用公共 `BlankLayout` 承载主题分区页面

### 页面层

- `web/src/views/HomeView.vue`
  - 首页改成“平台首页 + 主题分区入口”
  - 首期主题卡片来自配置，不再写死页面内容
- `web/src/views/themes/ThemeHubView.vue`
  - 新增主题分区页面
- `web/src/views/themes/ThemeDetailView.vue`
  - 新增主题详情页面
  - 展示主题上下文对象、标签、模块入口和阶段能力占位

### 导航与身份入口

- `web/src/layouts/AppLayout.vue`
  - 侧边栏新增“平台首页”“主题分区”
- `web/src/components/UserInfoComponent.vue`
  - 用户菜单新增“主题分区”
  - 文档中心改为读取世界线配置
- `web/src/views/LoginView.vue`
  - 登录页底部链接改为“主题分区 / 项目文档”
- `web/src/components/ChatSidebarComponent.vue`
  - 聊天侧边栏品牌兜底改为 `Worldline`

## 当前前端平台入口结构

- 首页：`/`
- 主题分区：`/themes`
- PoE 主题页：`/themes/poe`
- 智能体：`/agent`
- 图谱：`/graph`
- 知识库：`/database`

## 本轮未做的事情

- 没有把主题上下文透传到后端请求
- 没有接入 PoE 知识库数据
- 没有接入 PoE 问答模板
- 没有接入 PoE 图谱实体关系

## 校验情况

- 已做静态校验：
  - YAML 配置可解析
  - 新增主题页面文件存在
  - 本轮修改的关键文件不再包含上游文档主页硬编码链接
- 未做构建校验：
  - 当前终端环境缺少 `node`、`npm`、`pnpm`，无法执行前端构建

## 已知剩余风险

- `web/src/components/modals/BenchmarkGenerateModal.vue`
- `web/src/components/modals/BenchmarkUploadModal.vue`
- `web/src/components/FileUploadModal.vue`

以上文件仍残留上游帮助文档链接，但不属于本轮“平台层最小实现”的核心路径，后续可做一轮品牌清理。

## 下一步建议

优先做一轮“平台层收尾 + 轻量上下文透传设计”：

1. 清理前端剩余的 Yuxi 文案与帮助链接
2. 为 `/themes/:themeId` 与 `/agent` 之间建立最小主题上下文跳转约定
3. 再进入 PoE 知识导入与问答模板接线
