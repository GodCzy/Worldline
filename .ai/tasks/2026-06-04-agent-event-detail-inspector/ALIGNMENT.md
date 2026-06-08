# Agent Event Detail Inspector Alignment

更新时间：2026-06-04

## 目标

在 Agent 工作台的 `RUN EVENTS` 中新增事件详情 Inspector，让每条事件都能展开查看 evidence、tool、timeline、permission 和 run evidence 线索。

## 范围

- 只修改 `/worldline/agent` 前端视图。
- 点击事件时选中该事件并聚焦关联分支。
- 展示事件 ID、类型、actor、run id、branch、summary 和链接字段。
- 保持本地 preview 事件和真实后端事件共用同一详情面板。

## 不做

- 不修改后端 API。
- 不新增数据库 schema。
- 不新增依赖。
- 不做跨页面深跳转。

## 验收

- `RUN EVENTS` 中有选中态。
- 页面出现 `EVENT DETAIL` 面板。
- 面板显示 Evidence / Tool / Timeline / Permission / Run Evidence 明细。
- 构建和浏览器截图验证通过。
