# Phase 11 Evidence Retrieval Phase 3

更新时间：2026-06-02

## 当前阶段

本轮进入第三阶段：混合检索与证据回答。

本阶段在第二阶段的文档编译器和 EvidenceAnchor 底座上，补齐 chunk/evidence 绑定、Evidence 查询 API、证据化查询输出。

## 已落地

- `KnowledgeChunk`
  - 保存 `chunk_id`
  - 保存 `db_id`、`file_id`、`doc_version_id`
  - 保存 `evidence_ids`
  - 保存 chunk 文本和 metadata
- `KnowledgeObjectRepository`
  - `bind_chunks_to_latest_evidence()`
  - `decorate_retrieval_results()`
  - `list_evidence_anchors()`
  - `get_evidence_anchor()`
  - `list_chunks()`
- `MilvusKB`
  - 索引时绑定 chunk/evidence。
  - 查询时在 `include_evidence=True` 下回填 citations。
- `EvidenceQueryService`
  - 输出 `answer`
  - 输出 `claims`
  - 输出 `citations`
  - 输出 `route_trace`
- `knowledge_router`
  - `POST /knowledge/databases/{db_id}/query-evidence`
  - `GET /knowledge/databases/{db_id}/evidence-anchors`
  - `GET /knowledge/databases/{db_id}/evidence-anchors/{evidence_id}`
  - `GET /knowledge/databases/{db_id}/documents/{doc_id}/chunks`

## 设计边界

- 旧 `/query` 不改返回语义。
- Milvus collection 不强制加字段。
- 当前 sparse 路径使用 keyword/BM25 proxy 与 dense vector hybrid 融合，不迁移 Milvus sparse vector schema。
- Evidence 绑定保存在 PostgreSQL。
- 无 evidence 的检索结果允许降级，`route_trace.evidence_enriched=false`。
- claims 当前是 extractive claim，后续可接入更强 claim extractor。

## 已验证

- ruff：通过。
- pytest：`13 passed, 1 warning`。

## 后续边界

下一阶段可继续处理：

- Evidence UI。
- Worldline MCP Server 暴露。
- LLM claim extraction。
- Graph/Auto-Wiki/TemporalFact 绑定 evidence。
- Evaluation gate 的 evidence accuracy 指标。
