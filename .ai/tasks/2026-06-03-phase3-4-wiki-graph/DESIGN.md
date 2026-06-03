# Phase 3/4 Design

更新时间：2026-06-03

## Phase 3 LLM Wiki Mainline

`AutoWikiService` 继续从 evidence-bound chunks 构建页面，但页面 metadata 增强为：

- `outline`：STORM-lite 风格多视角 outline。
- `sections`：可引用章节摘要。
- `claims`：每条 claim 绑定 evidence ids。
- `citations`：EvidenceAnchor 候选引用。
- `disputes`：显式冲突/争议检测结果。
- `open_questions`：待人工验证问题。
- `review`：人工审核状态。
- `evidence_coverage`：claim/evidence 覆盖率。
- `rag_role`：RAG 仅作为 evidence candidate recall。

`WikiRepository.serialize_page` 将这些字段兼容地提升到响应顶层，同时保留完整 `metadata`。

## Phase 4 Temporal Evidence Graph

`KnowledgeGraphService` 保留现有本地 Postgres evidence graph 写入边界，新增 metadata 语义：

- `episodes` / `episode`：Graphiti 风格 source episode。
- `provenance`：file、chunk、doc version、evidence ids。
- `validity_window`：valid_from、valid_to、invalidated_at、basis。
- `graphiti_pattern`：entity、relationship、temporal fact 的模式标记。

新增只读能力：

- `detect_temporal_conflicts`
- `build_neo4j_projection`
- `GET /graph/conflicts`
- `GET /graph/neo4j-projection`

## 兼容策略

- 不改 protected route 的原有响应字段。
- 新字段全部作为 optional metadata 或只读扩展。
- MCP 现有 `worldline.update_graph` 继续调用同一 service boundary。

