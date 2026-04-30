# 世界线 Phase 23：v1.1 第一波前端展示层收口

## Goal

- 收拢 `v1.1` 第一波实施中的前端展示层可见问题
- 优先修正用户直接可见的乱码、旧文案、英文残留和不直观提示

## Stable Decisions

- 本轮修改仅落在前端展示层和低风险壳层文件
- 已完成的主要收口面包括：
  - `[web/src/views/HomeView.vue](D:/worldline/web/src/views/HomeView.vue)`
  - `[web/src/views/LoginView.vue](D:/worldline/web/src/views/LoginView.vue)`
  - `[web/src/views/themes/ThemeHubView.vue](D:/worldline/web/src/views/themes/ThemeHubView.vue)`
  - `[web/src/views/themes/ThemeDetailView.vue](D:/worldline/web/src/views/themes/ThemeDetailView.vue)`
  - `[web/src/views/GraphView.vue](D:/worldline/web/src/views/GraphView.vue)`
  - `[web/src/layouts/AppLayout.vue](D:/worldline/web/src/layouts/AppLayout.vue)`
  - `[web/src/components/UserInfoComponent.vue](D:/worldline/web/src/components/UserInfoComponent.vue)`
- 本轮主要完成了以下可见层收口：
  - 主页入口与行动按钮中文化
  - 主题分区页文案统一
  - PoE 主题页中 `Phase 6 / PoE Entry`、`Route / Link` 等英文残留替换为中文口径
  - 侧栏中的 `Dashboard` 替换为 `运营看板`
  - 用户菜单中深色模式提示去掉 `Beta`
  - 图谱页入口说明优化，降低用户误解
- 构建验证通过：
  - `pnpm build`

## Phase Judgment

- 当前阶段：
  - `v1.1` 实施阶段
- 当前子阶段：
  - 第一波前端展示层收口已完成
- 是否 ready 进入下一子波：
  - 是，可以进入下一波前端收口或开始更细的主链路回归
- 下一步最主要关注点：
  - 继续清理仍然可见的旧文案与展示层不统一问题
  - 结合人工回归检查 Agent / Graph / Dashboard 的实际首屏体验
