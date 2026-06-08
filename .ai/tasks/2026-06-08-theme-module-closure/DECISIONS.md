# Decisions

## 2026-06-08

- 主题模块继续走 `/api/system/themes` 和 `theme_modules.json`，不新增 schema。理由：本阶段是闭环和契约补齐，不需要数据库迁移。
- `knowledge`、`context`、`worldline` 三处同时保留知识库 ID。理由：兼容现有前端解析、外部 Agent payload 和历史模块数据。
- MCP 和 Workflow 从 always-on 能力改为默认启用但可关闭的 surface。理由：用户要求模块能力开关覆盖 Wiki/Graph/Timeline/Gate，同时后续交接明确提到 MCP/Workflow。
