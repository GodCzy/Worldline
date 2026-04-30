# 模块扩展

## 目标

Worldline 的长期目标不是只承载 PoE。

Phase 5 已经完成平台层与模块层的分界，Phase 6 的第一轮任务不再是继续做平台重构，而是把“模块如何接入平台”写成明确契约，并用一个受控的第二模块试点验证这套契约是否成立。

## 平台层与模块层边界

### 平台层负责
- branding
- routing
- navigation
- shared layout
- permissions
- shared context switching
- operational tooling
- 共享页面对模块能力的统一消费入口

### 模块层负责
- taxonomy
- metadata schema
- answer templates
- graph schema
- recommendation logic
- domain assets
- 模块私有数据和私有展示语义

规则：平台层只能消费模块通过 adapter / facade 暴露出来的能力，不能直接读取模块私有文件或模块原始结构。

## 当前共享层真实消费面

当前共享层对模块能力的真实消费面已经比较清晰，主要来自 `web/src/data/worldline/index.js` 暴露的 facade。

### 共享页面当前实际消费的能力
- `getWorldlineDefaultQuestion`
- `hasWorldlineAdapter`
- `resolveWorldlineAdapter`
- `getWorldlineDisplayLabel`
- `getWorldlineManifestSummary`
- `getWorldlineRecommendationCandidates`
- `getWorldlineRecommendationCandidateById`
- `getWorldlineGraphLoops`
- `getWorldlineGraphLoopById`
- `getWorldlineGraphDefaultKeyword`
- `getWorldlineThemeShowcaseMeta`
- `getWorldlineThemeShowcaseCandidates`
- `getWorldlineThemeShowcaseGraphs`
- `getWorldlineAgentContextView`

### 当前共享层真实消费者
- `web/src/views/themes/ThemeDetailView.vue`
- `web/src/views/worldline/WorldlineHubView.vue`
- `web/src/views/worldline/WorldlineWorkbenchView.vue`
- `web/src/views/AgentView.vue`
- `web/src/views/GraphView.vue`

这意味着 Phase 6 第一轮不需要重新发明契约，而是把这批已经被共享层稳定消费的方法，收敛成正式模块接入契约。

## Phase 6 模块接入契约骨架

模块接入分两层：主题元数据层和 worldline adapter 层。

### 1. 主题元数据层
由 `src/config/static/info*.yaml` 或等价配置提供，最小字段建议固定为：
- `id`
- `name`
- `subtitle`
- `description`
- `entry_route`
- `status`
- `tags`
- `highlights`

用途：
- 让 `/themes` 和 `/worldline` 能发现模块
- 让平台知道模块入口在哪里
- 提供主题分区和 Hub 页的基础展示信息

### 2. Worldline Adapter 层
由 `web/src/data/worldline/<module>WorldlineAdapter.js` 提供。

#### 必填字段
- `id`
- `defaultQuestion`

#### 必需方法
- `buildWorldline(question, themeContext, options)`
- `getDisplayLabel(value)`
- `getManifestSummary()`
- `getRecommendationCandidates()`
- `getRecommendationCandidateById(candidateId)`
- `getGraphLoops()`
- `getGraphLoopById(graphId)`
- `getGraphDefaultKeyword(graphLoopOrGraphId)`

#### 共享页强依赖的方法
这组方法已经被共享页真实消费，因此 Phase 6 应将其视为正式契约的一部分：
- `getThemeShowcaseMeta()`
- `getThemeShowcaseCandidates()`
- `getThemeShowcaseGraphs()`
- `getAgentContextView(activeContext)`

#### 当前仍建议保留的方法
- `getCardTitleById(cardId)`

## buildWorldline 的最小返回结构

`buildWorldline()` 的返回值必须能被 `worldlineContextStore.hydrate()` 直接消费。

最小字段建议固定为：
- `themeId`
- `moduleId`
- `rootQuestion`
- `questionDraft`
- `status`
- `generatedAt`
- `sourceType`
- `generationMode`
- `generationRound`
- `branches`
- `activeBranchId`
- `selectedNodeId`
- `tree`
- `viewState`
- `displayMeta`

其中：
- `branches` 负责“当前世界线分支”列表
- `tree` 负责工作台图形化展示
- `viewState` 负责 handoff 和最近一次生成来源
- `displayMeta` 负责阶段标题、分支数量、主题名称等页面文案

## 第二模块试点的最小能力面

Phase 6 第一轮不做第二模块的完整业务能力，只验证平台接入契约。

第二模块试点的最小能力面建议固定为：
- 能被 `/themes` 和 `/worldline` 发现
- 能提供 `defaultQuestion`
- 能提供基础 `buildWorldline()` 返回值
- 能在 `ThemeDetailView` 渲染最小 showcase 摘要
- 能在 `WorldlineWorkbenchView` 生成至少一组基础分支
- 能在 `AgentView` 生成可消费的最小上下文视图
- 不要求接入专用后端协议
- 不要求拥有完整 graph/database 管理能力
- 不要求一开始就支持复杂推荐逻辑

## 第二模块试点候选对象

### 首选候选：`worldline-ops`
推荐把第二模块试点定义为一个受控的“平台运营 / 验证知识模块”。

原因：
- 仓库里已经存在充足的运维、验证、阶段和证据语义，可直接作为静态样本来源
- 它不依赖新的后端协议或外部数据源
- 它最适合用来验证：
  - 模块发现
  - 模块路由
  - facade 消费
  - workbench 生成
  - agent handoff
- 它不会把 Phase 6 第一轮拖成“大功能扩张”

### 备选候选：`worldline-sandbox`
如果不想让第二模块带太多业务语义，可以用一个更轻的 sandbox 模块做契约试点。

适用场景：
- 只验证 adapter、路由和共享页消费
- 不验证真实业务深度
- 先把“平台是否支持第二模块”跑通，再决定下一个真实业务模块

## Phase 6 第一轮允许改动的范围

建议只允许改动：
- `src/config/static/info*.yaml`
- `web/src/data/worldline/index.js`
- `web/src/data/worldline/poeWorldlineAdapter.js`
- `web/src/stores/worldlineContext.js`
- `web/src/router/index.js`
- `web/src/views/themes/ThemeHubView.vue`
- `web/src/views/themes/ThemeDetailView.vue`
- `web/src/views/worldline/WorldlineHubView.vue`
- `web/src/views/worldline/WorldlineWorkbenchView.vue`
- `docs/module-extension.md`
- `docs/platform-architecture.md`

## Phase 6 第一轮明确不纳入的内容

- `server/**`
- `src/knowledge/**`
- `scripts/**`
- `test/**`
- `docs/archive/**`
- `artifacts/qa-*`
- `.playwright-cli`
- `test-results`
- `vendor-antdv` / `vendor-g6` 继续压缩
- graph/auth 契约重写
- 第二模块的大规模功能扩张

## 验证基线

Phase 6 第一轮必须继承 Phase 5 的基线：
- `pnpm --dir web build`
- `npm run docs:build`
- `/agent`、`/graph`、`/themes` 可达
- `/`、`/archive/` 可达

新增最小增量验证只看：
- 第二模块试点是否可被平台发现
- 第二模块是否遵守 facade 契约
- PoE 路径是否不回退
