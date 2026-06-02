# Phase 3 Evidence Retrieval Alignment

更新时间：2026-06-02

## 目标

完成 Worldline 第三阶段最小完整闭环：混合检索结果必须能够绑定证据，并输出可追溯的 `claims`、`citations` 和 `route_trace`。

## 范围

- 将检索 chunk 与 `EvidenceAnchor` 建立持久绑定。
- 提供 EvidenceAnchor 查询 API。
- 提供文档 chunk 查询 API，暴露 `evidence_ids`。
- 提供证据化查询 API，返回 `answer`、`claims`、`citations`、`route_trace`。
- 保持旧 `/knowledge/databases/{db_id}/query` 返回语义不变。

## 不做

- 不安装或启用新的高权限 MCP。
- 不引入真实外部 embedding/reranker 网络调用作为单测前提。
- 不做 Evidence UI、MCP Server 暴露、Neo4j/Auto-Wiki 证据绑定。
- 不强制迁移已有 Milvus collection schema。

## 验收标准

- `KnowledgeChunk` 表存在，能保存 `chunk_id -> evidence_ids`。
- `index_file()` 生成 chunk 后能 best-effort 绑定最新成功文档版本的 EvidenceAnchor。
- `/query-evidence` 能返回结构化 claim、citation 和 route_trace。
- EvidenceAnchor 和文档 chunks 可以分页查询。
- 单元测试和 ruff 通过。
- 真实 PostgreSQL smoke 能创建表并写入 chunk/evidence 绑定。
