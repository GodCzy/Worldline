# P2-5 产品规划升级

日期：2026-06-08

## 目标

把 Worldline 后续路线从零散功能清单升级为可执行产品/工程路线图，围绕 Evidence-backed LLM Wiki + Temporal Knowledge Graph OS 的核心形态，定义后续阶段、验收证据、风险边界和不做事项。

## 输入事实

- `docs/product/worldline-project-book.md`
- `docs/architecture/knowledge-compiler.md`
- `docs/architecture/llm-wiki.md`
- `docs/architecture/temporal-evidence-graph.md`
- `docs/architecture/worldline-ui.md`
- `docs/architecture/mcp-skill-governance.md`
- `docs/architecture/evaluation-gates.md`
- P0/P1/P2 已完成任务证据和 OutputMD 总结

## 边界

- 本任务只做规划文档，不改产品代码。
- 规划不得把 Worldline 降级成普通 RAG 聊天页。
- 不引入默认数据库直写 MCP、全盘 filesystem MCP 或未审计外部写工具。
- 不把 STORM/Graphiti/KAG/HippoRAG 等参考项目当作直接迁移目标。

## 验收

- 形成 `ROADMAP.md`。
- 覆盖 Wiki、Temporal KG、Worldline Branch Canvas、Agent Run Ledger、MCP/Skill Governance、Quality Gate Replay、Compact Console UX。
- 每条路线有验收证据和下一步最小切片。
- 写入 `D:\document\OutputMD` 总结。
