# Worldline Frontier Stack Alignment

更新时间：2026-06-03

## Goal

把 Worldline 重新定位为 Evidence-backed LLM Wiki + Temporal Knowledge Graph OS：

- LLM Wiki 和 Evidence Graph 是主产品形态。
- RAG 只作为证据回查、长尾召回和候选上下文补充层。
- UI 以可交互世界线、证据轨、时间变化和图谱推理为第一信号。

## Success Criteria

- 当前阶段事实源写入 `.ai/tasks/2026-06-03-worldline-frontier-stack/`。
- 新项目书和架构文档写入 `docs/product/` 与 `docs/architecture/`。
- 文档明确保留、引入、暂缓、禁止的技术栈。
- Phase 0 工程保护项落地：换行/编码保护、Docker context 忽略、live API 测试凭据不阻塞本地单测。
- 本地 Worldline Codex skills 创建并通过基础校验。

## Boundaries

- 不重写 Git 历史，不删除 `.git`。
- 不恢复旧 PoE/demo/旧规划内容。
- 不破坏现有 `/api/knowledge/databases/{db_id}/worldline/*`、wiki、graph、timeline、quality-gate、MCP tool contract 和前端 `/worldline` 路由。
- 不默认安装数据库直连写入 MCP，不把 token/API key 写进仓库或 Markdown。

## Audience

- Joy：作为项目 owner 和最终验收者。
- Codex / Claude / Antigravity：作为后续实现、审查、测试的协作 Agent。
- 未来贡献者：通过项目书、架构文档和 skills 快速理解 Worldline 不等于普通 RAG Chat。
