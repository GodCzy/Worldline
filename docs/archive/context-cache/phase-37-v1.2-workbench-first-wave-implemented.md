# phase-37 v1.2 世界线工作台首版实现收口

## 当前稳定结论

- `v1.2` 第一波实现已经从“路由和结构预埋”推进到“可运行工作台首版”。
- 平台层已经不再直接在工作台视图里 `import` PoE 适配器，而是通过 `web/src/data/worldline/index.js` 的 adapter registry 取能力。
- `/worldline/:themeId` 对未接入主题已进入 fail-closed：
  - 不再静默渲染 PoE 世界线数据
  - 会显示明确 unsupported state
- `WorldlineHubView` 现在只暴露已接入世界线适配器的模块，并通过 registry 提供默认问题文案。
- 继续生成后的 `EvidenceRail` duplicate key 警告已修补，避免列表更新不稳定。
- `themeContext` 已补入 `branch` 字段透传，便于世界线聚焦分支在跨页 handoff 时保留分支标识。

## 本轮实际改动

- 已在既有提交 `96508b7 feat(worldline): add registry-driven workbench fail-closed` 基础上继续收口：
  - `web/src/views/worldline/WorldlineHubView.vue`
  - `web/src/components/worldline/WorldlineEvidenceRail.vue`
  - `web/src/stores/themeContext.js`

## 验证结论

- 构建验证：
  - `cd D:/worldline/web && npm run build` 通过
- 浏览器 smoke：
  - 使用 Playwright 验证 `/worldline/poe`
  - 首屏可见世界线工作台、问题输入区、分支主舞台、节点详情、证据轨、下一步动作
  - 选择分支后右侧详情联动正常
  - 触发“沿这条主线继续生成”后进入下一轮聚焦生成
  - 点击“进入对话”在未登录态跳转到 `/login`
  - `/worldline/unknown` 显示 unsupported state，且不再出现 PoE 世界线内容
- 说明：
  - 本轮浏览器 smoke 使用了临时 mock backend，仅覆盖 `/api/system/health` 与 `/api/system/info`
  - 原因是当前本机缺少 `fastapi` 运行依赖，真实后端未能在本轮直接拉起

## MCP / 验证方式判断

- 本轮继续证明 Playwright MCP 对 `v1.2` 阶段是高价值能力：
  - 能直接验证 worldline 首屏语义是否成立
  - 能验证 unsupported theme 是否真正 fail-closed
  - 能在“构建通过”之外补到浏览器层行为证据

## 当前阶段判断

- 当前 phase：`v1.2 工作台首版实现收口`
- next phase readiness：`接近 ready，但还差真实后端环境下的一次 smoke`
- 进入下一阶段前的主要 gap：
  - 在真实后端依赖齐全的环境里完成一次 `/worldline/poe` 与 `/worldline/unknown` 的端到端 smoke
  - 判断游客态下 `AppLayout` 的无关 auth error 是否需要单独收口
