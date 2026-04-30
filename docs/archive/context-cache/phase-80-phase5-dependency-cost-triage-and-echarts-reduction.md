# Phase 80 - Phase 5 Dependency Cost Triage And Echarts Reduction

## Summary
- Phase 5 第七轮的目标是对剩余重依赖做成本分层，而不是继续无差别切 chunk。
- 本轮实际完成了一条有明确收益且局部可控的优化：把 dashboard 图表从 `echarts` 整包导入切换到 `echarts/core` 的按需注册。
- 结果是 `vendor-echarts` 从约 `1119 kB` 进一步降到约 `382 kB`，不再属于 `>500 kB` warning。
- 当前剩余的大包只剩两类：
  - `vendor-antdv` 约 `1477 kB`
  - `vendor-g6` 约 `1331 kB`
- 这两类已经更接近“特性成本”而不是“简单切分问题”。

## Actual Subagent Decomposition
本轮实际启动了 5 路子代理：
- `system_mapper`
- `product_architect`
- `frontend_worker`
- `backend_worker`
- `qa_release_auditor`

但它们都因额度限制中断，未能产出可引用结论。因此本轮的最终 mapping、design judgment 和 implementation 由 controller 在本地直接完成，并在这里显式记录为 controller-side synthesis。

## Mapping
### 1. `vendor-antdv`
主要来源：
- `D:\worldline\web\src\main.js` 中的 `app.use(Antd)` 全局插件注册
- 仓库中大量共享组件、视图与 store/composable 对 `ant-design-vue` 的广泛直接使用

判断：
- 继续压 `vendor-antdv` 已经不是低风险 manual chunk 问题。
- 若想再降，需要进入更高成本路径：
  - 放弃全局插件，改为显式组件注册/自动按需解析
  - 配套梳理全站 `a-*` 组件解析方式
- 该项暂判定为“当前接受的特性成本”，不在本轮继续动。

### 2. `vendor-g6`
主要来源：
- `D:\worldline\web\src\components\GraphCanvas.vue` 中对 `@antv/g6` 的静态依赖
- 其背后还会拉入 `@antv/*` 图谱运行时能力

判断：
- 这条线是图谱能力本身，不是简单冗余。
- 若想再降，需要评估：
  - 改成运行时动态 import
  - 或重新评估图谱渲染器选择
- 这已经超过“最小可行继续优化”的边界，因此本轮不动。

### 3. `vendor-echarts`
主要来源：
- `D:\worldline\web\src\components\dashboard\*.vue` 五个统计图表组件
- 之前统一使用 `import * as echarts from 'echarts'`

判断：
- 这是本轮最值得继续优化的一项，因为来源集中、行为边界清晰、改动局部。
- 适合改为 `echarts/core` + 按需图表/组件注册。

### 4. `vendor-mindmap`
主要来源：
- `D:\worldline\web\src\components\MindMapSection.vue` 中的 `markmap-lib` 与 `markmap-view`

判断：
- 上一轮切分后已经低于 `500 kB`，当前不再是 warning 项。
- 暂时接受为按需懒加载后的特性成本，不继续优化。

## Code Changes
### 1. New helper
- 新增 `D:\worldline\web\src\utils\echarts.js`
- 内容：只注册 dashboard 真正使用的 ECharts 能力：
  - `BarChart`
  - `LineChart`
  - `PieChart`
  - `GridComponent`
  - `LegendComponent`
  - `TooltipComponent`
  - `CanvasRenderer`

### 2. Dashboard widgets switched to the helper
以下 5 个组件从 `import * as echarts from 'echarts'` 改为使用共享 helper：
- `D:\worldline\web\src\components\dashboard\AgentStatsComponent.vue`
- `D:\worldline\web\src\components\dashboard\CallStatsComponent.vue`
- `D:\worldline\web\src\components\dashboard\KnowledgeStatsComponent.vue`
- `D:\worldline\web\src\components\dashboard\ToolStatsComponent.vue`
- `D:\worldline\web\src\components\dashboard\UserStatsComponent.vue`

行为变化：
- 页面功能、图表类型、交互行为不变。
- 只改变图表依赖装配方式。

### 3. Build chunk refinement
- 修改 `D:\worldline\web\vite.config.js`
- 变化：
  - 保持 `vendor-antdv` 合并 ant-design 及其图标，避免 circular chunk warning
  - 将 `zrender` 从 `vendor-echarts` 中拆分到 `vendor-zrender`

结果：
- `vendor-echarts` 再次下降，并与 `vendor-zrender` 分离。
- 构建 warning 从之前的 3 个大 vendor 进一步收敛到 2 个：`vendor-antdv` 与 `vendor-g6`。

## Validation
### Build
- `pnpm --dir D:\worldline\web build`
- `npm --prefix D:\worldline run docs:build`

### Reachability
本机入口可达性确认：
- `/agent` -> `200`
- `/graph` -> `200`
- `/themes` -> `200`
- `/` -> `200`
- `/archive/` -> `200`

## Measured Outcome
### Before This Round
- `vendor-antdv` 约 `1351 kB`
- `vendor-g6` 约 `1331 kB`
- `vendor-echarts` 约 `1119 kB`
- `vendor-mindmap` 约 `493 kB`

### After This Round
- `vendor-antdv` 约 `1477 kB`
- `vendor-g6` 约 `1331 kB`
- `vendor-echarts` 约 `382 kB`
- `vendor-zrender` 约 `178 kB`
- `vendor-mindmap` 约 `493 kB`

Interpretation:
- `echarts` 线已经被从 warning 项中移除。
- `mindmap` 继续低于 warning 门槛。
- 剩余 warning 只集中在：
  - `ant-design-vue`
  - `@antv/g6`

## Judgment
- 本轮“最小可行继续优化”已经完成。
- 再继续追求 warning 清零，已经不应该靠低风险 patch；否则会进入：
  - 全局 UI 组件注册方式重构
  - 图谱引擎装配方式重构
- 这些都不是本轮允许范围。

## Phase Judgment
- current phase: `Phase 5 / dependency cost triage and targeted reduction`
- readiness for next phase: `not ready yet`
- main remaining gap: `需要对 ant-design-vue 与 G6 做单独的性能策略决策，判断是否接受为特性成本或进入更高成本重构`
