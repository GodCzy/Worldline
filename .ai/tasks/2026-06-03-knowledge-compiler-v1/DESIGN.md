# Knowledge Compiler v1 Design

更新时间：2026-06-03

## 数据流

1. `KnowledgeBase.parse_file` 读取文件元数据和 processing params。
2. `DocumentCompiler.compile_file` 或 `compile_url` 生成 `CompiledDocument`。
3. `KnowledgeObjectRepository.persist_compiled_document` 写入 `SourceAsset`、`DocumentVersion`、`DocumentNode`、`EvidenceAnchor`。
4. 旧 Markdown 输出仍保存到 MinIO，兼容现有读取和 RAG 索引流程。
5. `bind_chunks_to_latest_evidence` 把后续 chunk 绑定到最近成功的 evidence anchors。

## 编译器设计

- Docling 优先使用 `document.iterate_items()` 的 reading order；如果不可用，回退到 `texts`、`tables`、`pictures`。
- 表格节点保留 `table_json`，图片节点保留 `image_ref`。
- 节点尽量定位 Markdown 里的 char span，并计算 1-based line span。
- 图片 caption 不一定出现在 Markdown，因此 image 节点优先用 `image_ref` 定位 span。
- stats 记录 node type、page、parser trace、fallback 和结构化节点数量。

## Repository 设计

- `persist_compiled_document` 每次写入新的 `DocumentVersion`，保留版本历史。
- `SourceAsset.metadata` 记录 latest doc version、latest stats、parser trace 和 parser version。
- `list_document_versions` 提供分页版本列表。
- `get_document_version` 返回单个版本的 parse_config、source metadata、nodes 和 evidence anchors。

## API 设计

新增只读兼容扩展：

- `GET /api/knowledge/databases/{db_id}/document-versions`
- `GET /api/knowledge/databases/{db_id}/document-versions/{doc_version_id}`

已有接口保持不变：

- `POST /api/knowledge/databases/{db_id}/query-evidence`
- `GET /api/knowledge/databases/{db_id}/evidence-anchors`
- `GET /api/knowledge/databases/{db_id}/evidence-anchors/{evidence_id}`
- `GET /api/knowledge/databases/{db_id}/documents/{doc_id}/chunks`

