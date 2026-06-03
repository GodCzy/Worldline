# Knowledge Compiler v1 Alignment

更新时间：2026-06-03

## 目标

完成 Phase 2 Knowledge Compiler v1，让来源文档进入 Worldline 时不再只被压成 Markdown 或 RAG chunk，而是形成可追踪、可版本化、可回放的结构化知识对象链：

```text
SourceAsset -> DocumentVersion -> DocumentNode -> EvidenceAnchor
```

## 验收标准

- Docling 是 PDF、Office、HTML 等格式的主解析入口。
- Markdown/TXT 保留为兼容输入和阅读输出，但不是唯一中间表示。
- 编译结果必须包含 parser、parser_version、content_hash、ast_hash、parse_config、parser_trace、stats。
- 文档节点必须保留 node_type、order、page、bbox、char span、line span metadata、table_json、image_ref。
- EvidenceAnchor 必须绑定 doc_version_id、node_id、source_uri、page、line span、char span、text_span、text_excerpt。
- 失败解析必须持久化 failed DocumentVersion、error_message、parser_trace 和 stats，不丢失失败证据。
- 后续 RAG chunk、Wiki、图谱和质量门禁通过 evidence_id 回连证据。

## 不做范围

- 不在 Phase 2 改数据库 schema。
- 不重写后端现有 API contract。
- 不把项目迁移到外部 RAGFlow、KAG、Graphiti 或 DeepWiki 壳。
- 不启用外部 Agent 直写数据库。

