# Phase 84 - Phase 6 Contract Skeleton And Pilot Candidate Decision

## Summary
- 本轮把 Phase 6 第一轮的“模块接入契约骨架”收敛成了可实施的最小规范。
- controller 最终明确：
  - 契约不是重新发明，而是把 `web/src/data/worldline/index.js` 已经稳定暴露的 facade 能力正式化。
  - 第二模块试点应优先选择一个受控、低耦合、无需后端新协议的对象。
- 推荐的第二模块试点对象是：`worldline-ops`。
- 备选对象是：`worldline-sandbox`。

## Actual Subagent Decomposition
本轮实际启动并回收了以下只读子代理：
- `system_mapper`
  - 结论：如果只看剩余结构债，它更倾向把下一阶段聚焦在前端性能/依赖成本治理。
- `product_architect`
  - 结论：Phase 6 最符合产品演进顺序的主线仍是 `模块层契约化 + 第二模块试点`。
- `frontend_worker`
  - 结论：前端当前无结构性阻塞；如果只看前端，它更倾向把下一阶段主线放在交互结构整理。
- `backend_worker`
  - 结论：后端当前无硬阻塞；如果只看后端，它更倾向把下一阶段主线放在 `src/knowledge` 模块边界收敛。
- `qa_release_auditor`
  - 结论：Phase 6 继承 Phase 5 验证基线即可，新增验证应只覆盖第二模块入口可发现、PoE 路径不回退和 facade 不被污染。

## Controller Synthesis
### 为什么本轮要把契约写成文档
- 仅有 `phase-83` 还不够，因为它只固定了阶段主线，没有把契约字段和真实消费面写成可执行规范。
- `docs/module-extension.md` 是最合适的用户侧契约文档；把骨架写进去，下一轮实施就不会再围绕“到底什么算模块接入”重复争论。

### 模块接入契约最小字段
分两层：
1. 主题元数据层
   - `id`
   - `name`
   - `subtitle`
   - `description`
   - `entry_route`
   - `status`
   - `tags`
   - `highlights`
2. worldline adapter 层
   - 必填字段：`id`、`defaultQuestion`
   - 必需方法：
     - `buildWorldline(question, themeContext, options)`
     - `getDisplayLabel(value)`
     - `getManifestSummary()`
     - `getRecommendationCandidates()`
     - `getRecommendationCandidateById(candidateId)`
     - `getGraphLoops()`
     - `getGraphLoopById(graphId)`
     - `getGraphDefaultKeyword(graphLoopOrGraphId)`
   - 共享页强依赖方法：
     - `getThemeShowcaseMeta()`
     - `getThemeShowcaseCandidates()`
     - `getThemeShowcaseGraphs()`
     - `getAgentContextView(activeContext)`

### buildWorldline 的最小能力面
返回值必须能直接被 `worldlineContextStore.hydrate()` 消费，至少包含：
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

### 第二模块试点的最小能力面
- 可被 `/themes` 与 `/worldline` 发现
- 提供 `defaultQuestion`
- 提供基础 `buildWorldline()` 返回值
- 能在 `ThemeDetailView` 渲染最小 showcase 摘要
- 能在 `WorldlineWorkbenchView` 生成至少一组基础分支
- 能在 `AgentView` 生成最小上下文视图
- 不要求接入后端新协议
- 不要求完整 graph/database 管理能力

### 推荐候选对象
#### 首选：`worldline-ops`
原因：
- 仓库内已有大量运维、验证、阶段与证据语义，可以作为静态样本直接复用。
- 低耦合、低风险，不要求新增后端协议。
- 能最直接验证“模块接入契约是否成立”。

#### 备选：`worldline-sandbox`
原因：
- 如果不想让第二模块承载过多真实业务语义，sandbox 更适合做纯契约验证。
- 风险更低，但产品证明力弱于 `worldline-ops`。

## Allowed Scope For Phase 6 Round 1
建议允许改动：
- `D:\worldline\src\config\static\info*.yaml`
- `D:\worldline\web\src\data\worldline\index.js`
- `D:\worldline\web\src\data\worldline\poeWorldlineAdapter.js`
- `D:\worldline\web\src\stores\worldlineContext.js`
- `D:\worldline\web\src\router\index.js`
- `D:\worldline\web\src\views\themes\ThemeHubView.vue`
- `D:\worldline\web\src\views\themes\ThemeDetailView.vue`
- `D:\worldline\web\src\views\worldline\WorldlineHubView.vue`
- `D:\worldline\web\src\views\worldline\WorldlineWorkbenchView.vue`
- `D:\worldline\docs\module-extension.md`
- `D:\worldline\docs\platform-architecture.md`

## Explicitly Excluded
- `D:\worldline\server\**`
- `D:\worldline\src\knowledge\**`
- `D:\worldline\scripts\**`
- `D:\worldline\test\**`
- `D:\worldline\docs\archive\**`
- `D:\worldline\artifacts\qa-*`
- `.playwright-cli`
- `test-results`
- `vendor-antdv` / `vendor-g6` 继续压缩
- graph/auth 契约重写
- 第二模块的大规模功能扩张

## Validation To Inherit
继承 Phase 5 基线：
- `pnpm --dir D:\worldline\web build`
- `npm --prefix D:\worldline run docs:build`
- `/agent`、`/graph`、`/themes` 可达
- `/`、`/archive/` 可达

第一轮新增最小验证：
- 第二模块试点入口可被平台发现
- 第二模块不污染共享层 facade
- 现有 PoE 路径不回退

## Phase Judgment
- current phase: `Phase 6 planning`
- readiness for next phase: `ready for Phase 6 round 1 implementation`
- main remaining gap: `在 worldline-ops 与 worldline-sandbox 之间确定试点对象，并把契约骨架落成最小代码补丁`
