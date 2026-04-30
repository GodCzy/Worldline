# Phase 83 - Phase 6 Module Contract And Second Module Pilot Baseline

## Summary
- Phase 6 最推荐的单一主线是：`模块层契约化 + 第二模块试点`。
- 选择这条主线的原因不是继续做局部优化，而是验证 Worldline 在 Phase 5 完成平台解耦之后，是否真的具备承载第二个知识模块的能力。
- Phase 6 不应再把 `vendor-antdv` 与 `vendor-g6` 当成未完成问题；它们仍保持为当前基线的已接受特性成本。
- Phase 6 的首轮目标不是扩功能，而是定义模块接入契约，并以一个受控的第二模块试点验证平台可复用性。

## Actual Subagent Decomposition
本轮实际启动并回收了以下只读子代理：
- `system_mapper`
  - 结论：Phase 5 已无明显必须继续停留在当前阶段的结构债；它更倾向把 Phase 6 主线放在前端性能/依赖成本治理。
- `product_architect`
  - 结论：Phase 6 最应进入 `模块层契约化 + 第二模块试点`，因为这最符合 Worldline 作为多域知识平台的演进顺序。
- `frontend_worker`
  - 结论：前端当前无结构性阻塞；如果只看前端，它更倾向把下一阶段主线放在交互结构整理，而不是继续追性能或抽象。
- `backend_worker`
  - 结论：后端当前无硬阻塞；如果只看后端，它更倾向把下一阶段主线放在 `src/knowledge` 模块边界收敛。
- `qa_release_auditor`
  - 结论：Phase 6 启动前的验证条件已经具备；下一阶段只需在 Phase 5 继承基线上增加最小增量验证。

## Controller Synthesis
### 为什么只推荐一个主线
- `system_mapper`、`frontend_worker`、`backend_worker` 的结论分别指向性能、交互、知识模块边界，但这些都更像“支撑性工作流”或“子问题”，缺少阶段级产品结果。
- `product_architect` 的结论更符合仓库当前产品目标：Worldline 已完成平台层与模块层分界，下一阶段最有价值的是证明平台不只服务 PoE，而是能承载第二模块。
- 因此 controller 采纳 `模块层契约化 + 第二模块试点` 作为 Phase 6 单一主线；性能、交互结构整理和后端边界收敛保留为该主线下的配套维度，而不是独立抢占阶段目标。

### 最推荐的单一主线
- `模块层契约化 + 第二模块试点`

### 为什么这条主线优先级最高
1. 它直接验证 Worldline 的长期产品目标：多域知识模块平台，而不是 PoE 单模块平台。
2. 它承接 Phase 5 的真实成果：既然平台边界已经稳定，下一步就该验证平台可复用，而不是继续做无止境的平台内循环优化。
3. 它能把前端交互、后端边界、文档和验证统一收敛到一个产品结果上：第二模块能否按统一契约接入。
4. 它比继续做性能或 docs 降噪更可验收，因为可以用“第二模块最小试点是否成功接入”来判断阶段完成度。

## Minimal First-Round Boundary
Phase 6 第一轮只建议做“契约定义 + 接入骨架”，不直接铺开第二模块全部业务能力。

### 建议纳入第一轮的文件/目录范围
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
- `D:\worldline\README.md` 仅在需要补充模块接入口径时最小更新

### 第一轮只做什么
- 明确模块接入契约：模块至少要提供什么能力，平台如何发现和使用它。
- 把当前 PoE adapter 总结成“契约样本”，而不是继续当作特例。
- 定义第二模块试点的最小能力面：
  - 模块 ID
  - 默认问题
  - 展示标签解析
  - 世界线/graph/recommendation 只读入口
  - 主题/工作台入口
- 明确平台侧允许消费的 facade 输出，不允许平台共享页直接消费模块私有结构。

## Explicitly Excluded From Phase 6 Round 1
以下内容明确不纳入 Phase 6 第一轮：
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
- 后端协议级重构
- 大规模第二模块功能扩张

## Validation Baseline To Inherit
Phase 6 第一轮必须继承 Phase 5 的验证基线：
- `pnpm --dir D:\worldline\web build`
- `npm --prefix D:\worldline run docs:build`
- 主入口可达：
  - `/agent`
  - `/graph`
  - `/themes`
- docs 入口可达：
  - `/`
  - `/archive/`

第一轮只需新增最小增量验证：
- 第二模块试点入口可被平台发现
- 第二模块不污染共享层 facade
- 现有 PoE 路径不回退

## MCP Judgment
- Phase 6 启动时不需要新增 MCP 作为前置条件。
- 继续复用已有 Playwright 进行浏览器 smoke 即可。
- 如果第二模块试点需要外部资料抽取或数据核对，再按需启用 Fetch / PostgreSQL MCP，而不是提前为“可能会用到”而安装。

## Phase Judgment
- current phase: `Phase 6 planning`
- readiness for next phase: `ready for Phase 6 round 1 implementation planning`
- main remaining gap: `把模块接入契约写成第一轮可实施的最小规范，并确定第二模块试点的具体对象`
