# Phase 3 Evidence Retrieval Decisions

更新时间：2026-06-02

## 决策 1：新增 `KnowledgeChunk` 而不是修改 Milvus schema

原因：

- 旧 Milvus collection 可能已经存在，强制改 schema 会破坏兼容。
- `EvidenceAnchor` 是 PostgreSQL 证据链对象，chunk/evidence 绑定也应在 PostgreSQL 可审计。
- 检索时可按 `chunk_id` 回填 citation。

## 决策 2：保留旧 `/query`

原因：

- 旧前端和 Agent 工具可能依赖 list 返回。
- 第三阶段结构化输出放到 `/query-evidence`，降低兼容风险。

## 决策 3：claims 先用 extractive 策略

原因：

- 当前没有稳定 claim extractor。
- extractive claim 可以确保每条 claim 都来自检索 chunk，并绑定 evidence_ids。
- 后续可在不改变 API 结构的前提下接入 LLM claim extraction。

## 决策 4：本阶段不启用新 MCP/Skill

原因：

- 第三阶段核心是本地后端数据链和 API，不需要 Figma/Notion/Filesystem MCP。
- MCP Inspector 只有在 Worldline MCP Server 暴露后才必要。
- Browser 截图等前端验证留到 Evidence UI 阶段。
