# 设计

## 样式策略

- 在 `DashboardView.vue` 根节点加 `layout-container wl-ant-dark`，复用已有暗色 Ant Design 基础变量。
- 在页面级 scoped CSS 中覆盖：
  - Ant Design card/table/input/select/button/pagination/statistic/divider。
  - 子组件常见 `stats-overview`、`mini-stat-card`、`chart-container`、`dashboard-card`。
- 保留现有网格布局和图表逻辑。

## 修正

- `cleanupCharts()` 中 `toolStatsRef` 分支误调用 `userStatsRef.cleanup()`，改为 `toolStatsRef.cleanup()`。
