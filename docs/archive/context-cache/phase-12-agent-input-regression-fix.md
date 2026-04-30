# 世界线 Phase 12 Agent Input Regression Fix

## Goal

- 修复登录后进入 `/agent` 页面无法输入文字的问题。
- 修复由于未选中智能体导致的省略号菜单不进入正常态的问题。
- 同步修正世界线品牌配置与 PoE 展示标签。

## Stable Decisions

- 根因不是输入框组件本身，而是 `/agent` 路由在没有 `:agent_id` 时没有保证选中默认智能体。
- 前端路由层现在会在已登录用户访问 `/agent` 时，自动解析并跳转到 `/agent/:agent_id`。
- 品牌配置继续从 `src/config/static/info.template.yaml` 下发，但文件内容已统一为世界线专属文案。
- PoE 展示标签继续走 `web/src/data/poePhase1.js`，但中文展示值已修正为可读文本。

## Allowed Files

- `web/src/router/index.js`
- `web/src/data/poePhase1.js`
- `src/config/static/info.template.yaml`
- `docs/context-cache/phase-12-agent-input-regression-fix.md`

## Blocked Files

- `src/knowledge/**`
- `src/agents/common/**`
- `src/services/chat_stream_service.py`
- 其他高风险后端运行链路

## Validation Snapshot

- `pnpm build` in `web/`: passed
- `docker compose up -d --build api web`: passed
- `POST /api/auth/token`: passed
- `GET /api/chat/default_agent`: returns `ChatbotAgent`
- 预期登录后访问 `/agent` 时会自动落到 `/agent/ChatbotAgent`

## Next Step

- 在浏览器里执行一次完整人工回归：登录、进入 `/agent`、验证输入框可聚焦可输入、验证省略号菜单可点击。
- 如果仍有异常，再定点修具体组件，不再回到大范围平台改造。
