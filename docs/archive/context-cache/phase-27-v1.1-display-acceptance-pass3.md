# Phase 27 - v1.1 第三波展示层验收前收口

## 阶段结论

- 当前仍处于 `v1.1` 实施阶段。
- 本轮继续只处理前端展示层和用户可见文案，没有扩功能，也没有进入 `v1.2+` 范围。
- 本轮的重点是为最终验收前整理继续降低页面理解成本，统一菜单、导航和操作口径。

## 本轮 subagent 结果

- `system_mapper`
  - 确认本轮安全写入面仍在：
    - `web/src/layouts/AppLayout.vue`
    - `web/src/views/DashboardView.vue`
    - `web/src/views/GraphView.vue`
    - `web/src/views/AgentView.vue`
    - `web/src/components/UserInfoComponent.vue`
  - 明确禁止深入 `AgentChatComponent`、`GraphCanvas`、API 与核心运行链。
- `frontend_worker`
  - 指出第三波最值得修的是：
    - `GraphView` 的技术感提示
    - `AgentView` 的菜单与上下文提示
    - `AppLayout` 的导航口径
    - `DashboardView` 的后台术语
- `qa_release_auditor`
  - 明确本轮验收重点：
    - 首屏是否看得懂
    - 菜单是否可用
    - 导航是否清晰
    - 不能出现可见乱码或“文案看不懂但功能存在”的情况

## 本轮稳定结果

- `AppLayout`
  - “平台首页”改为“首页”
  - “图谱”改为“知识图谱”
  - 仓库入口 tooltip 改为“项目仓库”
  - 调试弹窗标题改为“调试面板（非生产环境）”
- `AgentView`
  - “清空上下文”改为“清除主题上下文”
  - 输入区说明更直接：强调上方是说明区，真正输入框在底部
  - “当前配置”改为“正在使用的配置”
  - “分享对话”改为“导出对话”，与实际行为对齐
  - “新建配置”统一为“新建智能体配置”
- `GraphView`
  - “选择或输入知识库 ID”改为“选择或输入知识库编号”
  - “导出图谱数据”改为“导出当前图谱”
  - 上传说明从“仓库内示例文件”改为“项目文档中的导入说明”
  - 上传提示标题改为“知识图谱上传方式说明”
  - 非 Neo4j 提示文案改为更自然的用户口径
- `DashboardView`
  - “输入用户 ID”改为“输入用户编号”
  - “查看反馈详情”改为“查看反馈”
  - 列标题“用户”改为“用户编号”

## 边界判断

- 本轮实际改动仍完全处于 `v1.1` 安全写入面。
- 未触碰：
  - `src/knowledge/**`
  - `src/agents/common/**`
  - `src/services/chat_stream_service.py`
  - `AgentChatComponent` 核心聊天逻辑
  - `GraphCanvas` 与图谱数据交互逻辑

## 验证基线

- 前端构建通过：`pnpm build`
- 文档构建通过：`npm run docs:build`
- HTTP smoke 通过：
  - `/`
  - `/dashboard`
  - `/graph`
  - `/agent/ChatbotAgent`
  - `/themes/poe`
  - `/api/system/health`

## 下一步判断

- 当前仍处于 `v1.1` 实施阶段。
- 已 ready 进入 `v1.1` 最终验收前整理。
- 当前最主要剩余 gap 是：
  - 少量低风险页面或组件可能还有残余旧文案
  - 需要一次面向全主链路的最终验收清单与人工回归
  - 但展示层主阻塞项已明显减少
