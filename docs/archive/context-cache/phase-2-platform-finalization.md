# 世界线 Phase 2 Platform Finalization

## Goal

完成平台层收尾，不进入 PoE 知识导入。

## Stable Decisions

- `/themes/poe` 到 `/agent` 的最小主题上下文约定采用前端路由 query:
  - `theme`
  - `module`
  - `scene`
  - `version`
- 新增前端 `themeContext` store 作为页面层共享上下文，不侵入后端核心服务。
- 剩余上游帮助链接全部改为世界线本地文档页 `06-platform-operations`。
- 本地 `.env` 已切换为真实 `SILICONFLOW_API_KEY`，并已重建 `api` / `worker`。

## Validation Snapshot

- Docker Compose 全部核心服务已启动，`api` 为 healthy。
- 前端入口路由可访问：
  - `/`
  - `/themes/poe`
  - `/dashboard`
- 文档站已可本地构建：`npm run docs:build`
- 后台链路已验证：
  - 初始化本地 superadmin 成功
  - `/api/dashboard/stats` 可正常返回
- 模型链路已验证：
  - `/api/chat/call` 可返回真实模型响应
- Agent 链路已验证到流式首块：
  - `POST /api/chat/agent/ChatbotAgent` 返回 `200`
  - 首个流式 chunk 含 `status=init`
  - `meta` 中已带 `theme/module/scene/version`

## Allowed Files

- `web/src/views/themes/ThemeDetailView.vue`
- `web/src/views/AgentView.vue`
- `web/src/stores/themeContext.js`
- `web/src/stores/info.js`
- `web/src/components/modals/BenchmarkGenerateModal.vue`
- `web/src/components/modals/BenchmarkUploadModal.vue`
- `web/src/components/FileUploadModal.vue`
- `docs/.vitepress/config.mts`
- `docs/06-platform-operations.md`

## High-Risk Files Still Untouched

- `src/knowledge/base.py`
- `src/knowledge/manager.py`
- `src/knowledge/implementations/lightrag.py`
- `src/agents/common/base.py`
- `src/agents/chatbot/graph.py`
- `src/services/chat_stream_service.py`
- `src/services/agent_run_service.py`

## Next Step

进入 PoE 模块层设计与最小实现：

1. 明确 PoE taxonomy 与 metadata schema
2. 设计首批知识导入样例
3. 让主题上下文开始约束知识库与问答模板
