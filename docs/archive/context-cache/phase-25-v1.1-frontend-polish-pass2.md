# 世界线 Phase 25：v1.1 第二波前端展示层收口

## Goal

- 继续收口 `Agent / Graph / Dashboard` 三个主页面中剩余的可见文案、说明提示和页面理解成本
- 保持修改只停留在前端页面壳层与低风险展示逻辑
- 不把 `v1.1` 的展示层收口扩散成核心功能改造

## Subagent Results

### `system_mapper`

- 再次确认本轮安全写入面主要在：
  - `[web/src/views/AgentView.vue](D:/worldline/web/src/views/AgentView.vue)`
  - `[web/src/views/GraphView.vue](D:/worldline/web/src/views/GraphView.vue)`
  - `[web/src/views/DashboardView.vue](D:/worldline/web/src/views/DashboardView.vue)`
- 明确不应进入：
  - `AgentChatComponent`
  - `GraphCanvas`
  - API 层
  - `src/knowledge/**`
  - `src/agents/common/**`
  - `src/services/chat_stream_service.py`

### `frontend_worker`

- 建议本轮继续收口：
  - `AgentView` 的上下文说明口径
  - `GraphView` 的标题、导入说明、输入提示
  - `DashboardView` 的进入体验和页面说明

### `qa_release_auditor`

- 把本轮人工回归重点收敛到：
  - `Agent` 首屏输入区可见且语义清楚
  - `Graph` 页面空态、搜索框和当前闭环提示可理解
  - `Dashboard` 首页进入后首屏有主体内容，且没有无意义成功提示干扰

## Stable Changes

- `[AgentView.vue](D:/worldline/web/src/views/AgentView.vue)`
  - 将“清除”改为“清空上下文”
  - 将“推荐欢迎提示”改为“推荐引导”
  - 进一步明确说明：上方区域不是输入区，真正输入框在页面底部
  - 复制建议提问后的提示更直观
- `[GraphView.vue](D:/worldline/web/src/views/GraphView.vue)`
  - 为页面标题补充说明文案
  - 将“添加到图数据库”统一为“添加到知识图谱”
  - 将开发者视角的示例路径说明改为用户可理解的导入格式说明
- `[DashboardView.vue](D:/worldline/web/src/views/DashboardView.vue)`
  - 新增“运营总览”说明区
  - 移除页面加载成功时的无意义 toast，降低进入页面时的干扰感

## Validation Baseline

- `pnpm build` 通过
- `npm run docs:build` 通过
- HTTP smoke：
  - `/agent/ChatbotAgent` -> `200`
  - `/graph` -> `200`
  - `/dashboard` -> `200`
  - `/api/system/health` -> `200`

## Manual Checks

- `Agent`
  - 首屏可看懂哪里是上下文说明区，哪里是真正输入区
  - “清空上下文”按钮文案更直观
- `Graph`
  - 页面标题和说明能帮助理解当前页面用途
  - 上传知识文件的说明不再直接暴露仓库示例路径
- `Dashboard`
  - 进入页面时不再弹“数据加载成功”
  - 顶部“运营总览”说明有助于理解看板用途

## Phase Judgment

- 当前阶段：
  - `v1.1` 实施阶段
- 当前子阶段：
  - 第二波前端展示层收口
- 是否 ready 进入下一子波：
  - 是，当前主链路展示层已经进一步稳定，可以进入第二波剩余低风险页面与组件清理
- 当前最主要剩余缺口：
  - 还存在少量用户菜单、辅助组件和个别页面提示的细节可继续统一，但不再是主链路阻塞项
