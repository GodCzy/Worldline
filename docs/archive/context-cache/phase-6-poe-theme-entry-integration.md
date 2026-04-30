# 世界线 Phase 6 PoE Theme Entry Integration

## Goal

把 PoE 的推荐候选和图谱闭环以低风险方式接入 `/themes/poe`，并把用户选择写入现有 `themeContext`。

## Stable Decisions

- 前端新增一个本地数据适配模块：
  - `web/src/data/poePhase1.js`
- `/themes/poe` 现在会直接消费：
  - `data/poe/processed/recommendation/phase1-candidates.json`
  - `data/poe/processed/graph/*.json`
  - `data/poe/processed/cards/manifest.json`
- `themeContext` 扩展了以下低风险字段：
  - `focus`
  - `candidate`
  - `graph`
  - `build`
  - `entry`
- 推荐候选会把选择写入 `themeContext` 后再进入 `/agent`
- 图谱闭环会把选择写入 `themeContext`
  - 管理员进入 `/graph`
  - 非管理员回退到带上下文的 `/agent`
- Agent 页顶部上下文条已改成中文。

## Allowed Files

- `web/src/data/poePhase1.js`
- `web/src/stores/themeContext.js`
- `web/src/views/themes/ThemeDetailView.vue`
- `web/src/views/AgentView.vue`
- `docs/context-cache/phase-6-poe-theme-entry-integration.md`

## High-Risk Files Still Blocked

- `src/knowledge/base.py`
- `src/knowledge/manager.py`
- `src/knowledge/implementations/lightrag.py`
- `src/agents/common/base.py`
- `src/agents/chatbot/graph.py`
- `src/services/chat_stream_service.py`
- `src/services/agent_run_service.py`

## Validation Snapshot

- `web` 前端依赖已在本机通过 `pnpm install --frozen-lockfile` 补齐
- `pnpm build` 已通过
- `http://localhost:5173/themes/poe` 返回 `200`

## Next Step

1. 把 `/themes/poe` 上的推荐选择真正联动到 Agent 输入区或欢迎提示
2. 让 `/graph` 页读取当前 `themeContext.graph`
3. 再考虑把推荐候选和图谱闭环接到后台 API 或真实图数据库
