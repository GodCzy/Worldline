# Phase 26 - v1.1 展示层文案与可理解性收尾

## 阶段结论

- 当前仍处于 `v1.1` 实施阶段。
- `v1.1` 的定位仍是“平台稳定化与治理化版本”，本轮没有扩功能，没有进入 `v1.2+` 范围。
- 本轮继续收口了登录页、主题分区页、主题详情页和用户头像菜单中的残余旧文案与不直观提示。

## 本轮稳定结果

- 用户头像菜单中的文档入口统一为“文档中心”。
- 登录页底部入口文案统一为“文档中心”。
- 主题分区页说明从架构口径改为用户口径，更强调“进入主题后会持续保留当前主题上下文”。
- 主题详情页进一步降低技术感：
  - 顶部文档按钮改为“查看模块文档”
  - “当前能力占位”改为“当前模块能力”
  - “模块入口”改为“可用入口”
  - “路由 / 外链”改为“页面入口 / 外部链接”
  - 新增“当前主题上下文”说明文字，明确后续页面如何使用主题、推荐和图谱信息
  - 去掉对内部实现名词的直接暴露，保留用户可理解表述

## 边界判断

- 本轮改动仍然只落在低风险前端展示层：
  - `web/src/components/UserInfoComponent.vue`
  - `web/src/views/LoginView.vue`
  - `web/src/views/themes/ThemeHubView.vue`
  - `web/src/views/themes/ThemeDetailView.vue`
- 未触碰高风险核心层：
  - `src/knowledge/**`
  - `src/agents/common/**`
  - `src/services/chat_stream_service.py`

## 验证基线

- 前端构建通过：`pnpm build`
- 文档构建通过：`npm run docs:build`
- 关键页面可访问：
  - `/login`
  - `/themes`
  - `/themes/poe`
  - `/agent/ChatbotAgent`
  - `/graph`
- 后端健康检查可访问：`/api/system/health`

## 下一步判断

- 项目仍处于 `v1.1` 实施阶段。
- 已 ready 进入 `v1.1` 的下一子波或最终验收前整理。
- 当前最主要剩余 gap 是：
  - 少量低风险组件仍可能残留旧文案
  - 页面内引导还可以继续统一
  - 但主链路已经不再被展示层问题阻塞
