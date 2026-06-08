# Agent Workbench Event Timeline Alignment

更新时间：2026-06-04

## 目标

把 Agent 工作台中的 run ledger 事件从左侧按钮计数升级为右侧可审查时间线，让 Worldline 的“任务可回放”更具体。

## 范围

- 在 `/worldline/agent` 右侧 inspector 中新增 `RUN EVENTS` 面板。
- 使用已有 `ledgerEvents` 和后端事件字段：`eventType`、`actor`、`branchId`、`summary`、`createdAt`。
- 无后端事件时显示本地预览事件，确保后端暂不可用时仍能看到产品形态。
- 支持按 all/run/branch/tool/skill 过滤事件。
- 事件绑定 `branchId` 时允许点击聚焦对应分支。

## 不做

- 不修改 run ledger 后端 API。
- 不新增数据库 schema。
- 不新增前端依赖。
- 不做管理员登录态 E2E，因为当前没有可安全注入的管理员凭据。

## 验收

- 页面中可见 `RUN EVENTS` 面板。
- 本地预览态至少显示 run、branch、tool、skill 类事件。
- 后端事件刷新后可替换为真实事件。
- 构建通过，浏览器截图无明显布局断裂。
