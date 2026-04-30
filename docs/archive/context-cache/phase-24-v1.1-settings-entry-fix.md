# 世界线 Phase 24：v1.1 系统设置入口修复

## Goal

- 修复用户头像菜单中的“系统设置”在部分页面点击无反应的问题
- 保持修复范围只落在前端展示层入口与弹窗外壳
- 不进入系统设置内部配置链和高风险核心层

## Root Cause

- `[UserInfoComponent.vue](D:/worldline/web/src/components/UserInfoComponent.vue)` 被复用于多种页面布局
- 在 `[AppLayout.vue](D:/worldline/web/src/layouts/AppLayout.vue)` 内部使用时，组件可以通过 `inject('settingsModal')` 拿到上层提供的弹窗控制 API
- 但在首页等不经过 `AppLayout` 的场景中，组件依旧显示“系统设置”菜单项，却拿不到注入对象
- 原实现对此静默失败，导致用户点击后没有任何反馈

## Stable Fix

- 保留已有的上层注入式系统设置弹窗打开方式
- 为 `[UserInfoComponent.vue](D:/worldline/web/src/components/UserInfoComponent.vue)` 增加本地 fallback：
  - 如果拿到上层 `settingsModal` API，则继续走原路径
  - 如果没有拿到注入，则在当前组件内直接挂载 `[SettingsModal.vue](D:/worldline/web/src/components/SettingsModal.vue)` 并打开
- 同步清理头像菜单和设置弹窗中用户可见的旧文案与不统一提示

## Allowed Files

- `[web/src/components/UserInfoComponent.vue](D:/worldline/web/src/components/UserInfoComponent.vue)`
- `[web/src/components/SettingsModal.vue](D:/worldline/web/src/components/SettingsModal.vue)`

## Explicit Non-Goals

- 不修改系统设置内部真实配置逻辑
- 不修改模型配置、用户管理、部门管理的数据写入链
- 不触碰：
  - `src/knowledge/**`
  - `src/agents/common/**`
  - `src/services/chat_stream_service.py`

## Validation Baseline

- `pnpm build` 通过
- 首页、运营看板、Agent 页可返回 `200`
- 手动验证以下页面中的头像菜单：
  - 首页
  - Agent 页
  - Graph 页
  - Dashboard 页
- 点击“系统设置”后，至少应打开可见弹窗，不应再出现无反应

## Phase Judgment

- 当前阶段：
  - `v1.1` 实施阶段
- 当前子阶段：
  - 第二波展示层与菜单交互收口
- 是否 ready 进入下一子波：
  - 是，当前修复已稳定，可以继续收口 Agent / Graph / Dashboard 剩余展示层细节
- 当前最主要剩余缺口：
  - 系统设置入口已修复，但设置页内部是否足够“产品化可理解”仍可继续优化
