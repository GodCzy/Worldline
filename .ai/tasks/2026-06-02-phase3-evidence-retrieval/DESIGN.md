# Phase 3 Evidence Retrieval Design

更新时间：2026-06-02

## 数据模型

新增 `KnowledgeChunk`：

- `chunk_id`
- `db_id`
- `file_id`
- `doc_version_id`
- `chunk_index`
- `text`
- `contextual_text`
- `evidence_ids`
- `metadata`

它是 Milvus 检索 chunk 与 PostgreSQL 证据链之间的桥接表。Milvus collection 不强制新增字段，避免破坏旧 collection。

## 写入链路

1. `parse_file()` 已在第二阶段写入 `DocumentVersion`、`DocumentNode`、`EvidenceAnchor`。
2. `MilvusKB.index_file()` 读取 Markdown 并生成 chunks。
3. `KnowledgeObjectRepository.bind_chunks_to_latest_evidence()` 读取同一文件最新成功 `DocumentVersion` 的 anchors。
4. 仓储用文本包含关系匹配 evidence；无匹配时按 chunk 顺序做 fallback。
5. 绑定结果写入 `KnowledgeChunk`。

## 查询链路

1. 旧 `/query` 保持返回列表。
2. 新 `/query-evidence` 调用 `EvidenceQueryService`。
3. `EvidenceQueryService` 调用现有 `knowledge_base.aquery()`，并强制 `include_evidence=True`。
4. 仓储按 `chunk_id` 回填 `evidence_ids` 与 citation 摘要。
5. 服务层构造 extractive `answer`、`claims`、`citations`、`route_trace`。

## 检索与模型契约

- dense：沿用 Milvus embedding 向量检索。
- sparse：当前使用 keyword/BM25 proxy，不迁移 Milvus sparse vector schema。
- hybrid：合并 dense 与 sparse_keyword 结果并按分数排序。
- embedding 候选：配置中已有 Qwen3 Embedding 与 BGE。
- reranker 候选：配置中已有 BGE reranker 与 Qwen3 rerank。
- route_trace 记录 `channels`、`sparse_strategy`、`embedding_model`、`reranker_model`。

## API

- `POST /api/knowledge/databases/{db_id}/query-evidence`
- `GET /api/knowledge/databases/{db_id}/evidence-anchors`
- `GET /api/knowledge/databases/{db_id}/evidence-anchors/{evidence_id}`
- `GET /api/knowledge/databases/{db_id}/documents/{doc_id}/chunks`

## 降级策略

- 如果 PostgreSQL 证据绑定失败，Milvus 索引和检索继续返回原 chunks。
- 如果非 Milvus 知识库返回 dict 风格结果，服务层尝试归一化 `result/chunks/data.chunks`。
- 如果检索结果没有 evidence，`claims/citations` 可以为空，`route_trace.evidence_enriched=false`。
