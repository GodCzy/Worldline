# Phase 81 - Phase 5 Antdv And G6 Cost Decision With Active-Tab Graph Deferral

## Summary
- Phase 5 第八轮的目标不是继续盲目追求 warning 清零，而是对 `vendor-antdv` 与 `vendor-g6` 做成本判断，并只落一项低风险的继续优化。
- 本轮结论：
  - `vendor-antdv` 当前应接受为平台 UI 的特性成本。
  - `vendor-g6` 当前应接受为图谱能力的特性成本。
  - 仍然存在一项低风险 runtime 优化：数据库详情页未激活图谱 tab 时，不应提前装载 `GraphCanvas`。
- 因此本轮只做了一项继续优化：把数据库详情页的图谱画布延迟到 graph tab 激活时才异步加载。

## Actual Subagent Decomposition
本轮实际启动了 5 路子代理：
- `system_mapper`
- `product_architect`
- `frontend_worker`
- `backend_worker`
- `qa_release_auditor`

但五路子代理都因为额度限制报错，没有形成可引用结果。本轮的 mapping、design judgment、implementation 与 validation 最终由 controller 本地完成，并在这里显式标记为 controller-side synthesis。

## Mapping
### 1. `vendor-antdv`
真实来源链路：
- `D:\worldline\web\src\main.js` 的 `app.use(Antd)` 全局插件注册
- 仓库中大量共享组件和页面直接使用 `a-*` 组件与 `ant-design-vue` API

判断：
- 这是平台 UI 组件体系的横向依赖，不是单一页面膨胀。
- 若继续优化，必须进入更高成本方案：
  - 改掉全局插件注册
  - 引入自动按需注册/解析
  - 或逐步改造大量模板级组件依赖
- 这已经超出本轮“最小可行继续优化”边界。
- 因此：`vendor-antdv` 本轮正式接受为特性成本。

### 2. `vendor-g6`
真实来源链路：
- `D:\worldline\web\src\components\GraphCanvas.vue` 对 `@antv/g6` 的静态依赖
- `GraphCanvas` 被 `GraphView.vue` 和 `KnowledgeGraphSection.vue` 使用

判断：
- 这不是冗余依赖，而是知识图谱渲染能力本身。
- 若继续压缩，需要进入更高成本路径：
  - 动态装配图谱渲染器
  - 或重新评估图谱引擎
- 在当前阶段，不应为清 warning 而贸然改动图谱装配层。
- 因此：`vendor-g6` 本轮也接受为特性成本。

## Minimal Viable Optimization Implemented
### `KnowledgeGraphSection.vue`
- 把 `GraphCanvas` 改为 `defineAsyncComponent()` 异步组件。
- 只有在 `active === true` 时才真正渲染 `GraphCanvas` 与 `GraphDetailPanel`。

行为变化：
- 在数据库详情页里，如果用户还没有切到 graph tab，就不会提前装载图谱画布。
- `/graph` 独立页面行为不变。
- 图谱查询、节点点击、边点击、详情浮层逻辑不变。

这项优化的目标不是继续降低 `vendor-g6` 的 chunk warning，而是避免数据库详情页在未进入图谱 tab 时过早拉起图谱运行时能力。

## Validation
### Build
- `pnpm --dir D:\worldline\web build`
- `npm --prefix D:\worldline run docs:build`

### Reachability
- `/agent` -> `200`
- `/graph` -> `200`
- `/themes` -> `200`
- `/` -> `200`
- `/archive/` -> `200`

## Measured Outcome
- 本轮前：
  - `vendor-antdv` 约 `1477 kB`
  - `vendor-g6` 约 `1331 kB`
- 本轮后：
  - `vendor-antdv` 约 `1477 kB`
  - `vendor-g6` 约 `1331 kB`

Interpretation:
- warning 数量没有继续下降。
- 这是预期结果，因为本轮做的是 runtime deferral，不是依赖包体拆分。
- 但这轮把 `KnowledgeGraphSection` 的重依赖触发条件从“进入数据库详情页”收紧为“真正激活 graph tab”。

## Judgment
- `vendor-antdv` 与 `vendor-g6` 都已经不再适合用低风险 patch 继续压缩。
- 它们要么被正式接受为当前阶段的特性成本，要么进入单独的高成本性能策略回合。
- 本轮完成后，Phase 5 的性能清理已经接近可收口状态。

## Phase Judgment
- current phase: `Phase 5 / cost acceptance and runtime deferral tightening`
- readiness for next phase: `almost ready`
- main remaining gap: `决定是否接受 Antdv 与 G6 为当前基线的特性成本；若接受，Phase 5 可以准备最终收口`
