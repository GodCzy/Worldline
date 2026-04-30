# 世界线 Phase 7 Agent Graph Context Surface

## Goal

让 `/agent` 和 `/graph` 更明确地表露当前 PoE 推荐或图谱闭环选择，但仍然只停留在平台层页面与 store。

## Stable Decisions

- 前端数据适配层 `web/src/data/poePhase1.js` 新增了查询辅助：
  - `getRecommendationCandidateById`
  - `getPoeDisplayLabel`
- `/agent` 现在会根据 `themeContext` 中的：
  - `candidate`
  - `graph`
  展示更明确的说明卡片，而不只是通用上下文字符串。
- `/graph` 现在会读取 `themeContext.graph`，并在页面顶部展示当前闭环标题、聚焦场景、节点数和边数。
- `GraphView` 会通过路由 query 同步 `themeContext`，支持从 `/themes/poe` 带参进入后直接识别当前闭环。

## Allowed Files

- `web/src/data/poePhase1.js`
- `web/src/views/AgentView.vue`
- `web/src/views/GraphView.vue`
- `docs/context-cache/phase-7-agent-graph-context-surface.md`

## High-Risk Files Still Blocked

- `src/knowledge/base.py`
- `src/knowledge/manager.py`
- `src/knowledge/implementations/lightrag.py`
- `src/agents/common/base.py`
- `src/agents/chatbot/graph.py`
- `src/services/chat_stream_service.py`
- `src/services/agent_run_service.py`

## Validation Snapshot

- `pnpm build` 在 `web/` 目录已通过
- `http://localhost:5173/themes/poe` 返回 `200`
- `http://localhost:5173/graph?...graph=poe-necromancer-minion-loop` 返回 `200`

## Next Step

1. 让 `/graph` 根据当前闭环自动切换更合适的默认查询
2. 让 `/agent` 在欢迎区或首轮提示中消费当前推荐候选
3. 再考虑把推荐与图谱上下文接到后台查询参数
