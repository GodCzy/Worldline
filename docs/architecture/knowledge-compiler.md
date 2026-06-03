# Knowledge Compiler Architecture

更新时间：2026-06-03

## Intent

Knowledge Compiler 把来源编译为可验证知识对象，而不是把文本直接切块塞进 RAG。

## Pipeline

```text
SourceAsset
  -> DocumentVersion
  -> DocumentNode
  -> EvidenceAnchor
  -> KnowledgeChunk
  -> WikiPage
  -> KnowledgeEntity / KnowledgeRelationship / TemporalFact
  -> QualityGateRun
```

## Rules

- Docling 是主解析入口，保留结构化 block、table、figure、heading、page span 和 reading order。
- Markdown 只是导出和阅读格式，不是唯一中间表示。
- 每个 chunk、Wiki 段落、实体、关系、时间事实都应能绑定 evidence ids。
- 解析失败、OCR fallback、模型抽取失败都必须记录错误和重试证据。
- Source hash、parser version、parse config、stats 是可回放必需字段。

## Phase 2 Implementation

当前 v1 实现已经落在以下边界：

- `DocumentCompiler` 产出 `CompiledDocument`，包含 `nodes`、`evidence_anchors`、`parser_trace`、`stats`、`content_hash` 和 `ast_hash`。
- Docling 文档优先使用 ordered items；不可用时回退到 `texts`、`tables`、`pictures`。
- `DocumentNode` 保留 node type、order、page、bbox、char span、table JSON、image ref；line span 同步进入 metadata。
- `EvidenceAnchor` 保留 page、line span、char span、text span、excerpt、confidence 和 provenance metadata。
- `KnowledgeObjectRepository` 写入 `SourceAsset`、`DocumentVersion`、`DocumentNode`、`EvidenceAnchor`，并把 latest compile metadata 回写到 `SourceAsset.metadata`。
- 编译失败也写入 failed `DocumentVersion`，保留 `error_message`、`parser_trace` 和失败 stats。
- 新增只读版本接口：`GET /api/knowledge/databases/{db_id}/document-versions` 和 `GET /api/knowledge/databases/{db_id}/document-versions/{doc_version_id}`。

## Stats Contract

`DocumentVersion.stats` 至少包含：

- `node_count`
- `evidence_anchor_count`
- `character_count`
- `table_count`
- `image_count`
- `node_type_counts`
- `page_count`
- `page_start`
- `page_end`
- `parser`
- `parser_trace_count`
- `parser_success_count`
- `parser_failure_count`
- `fallback_used`
- `structured_node_count`
- `has_docling_structure`
- `duration_ms`

## Retrieval Role

RAG 只做：

- evidence candidate recall；
- long-tail query fallback；
- Wiki/Graph 生成时的上下文补充；
- 质量门禁中的覆盖率和失败回放。

RAG 不负责定义 Worldline 的信息架构、主界面或可信度。
