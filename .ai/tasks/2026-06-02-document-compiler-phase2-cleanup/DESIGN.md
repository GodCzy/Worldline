# Design

更新时间：2026-06-02

## 文档编译器设计

新增 `src/knowledge/compiler/` 作为第二阶段的中间层。它不替代旧解析链，而是输出一个更完整的 `CompiledDocument`：

- `markdown_content`：继续供旧 MinIO `parsed.md` 和 LightRAG 入库使用。
- `nodes`：Document AST 节点，覆盖 heading、paragraph、table、image、bbox、page、char range。
- `evidence_anchors`：从可引用节点派生的 EvidenceAnchor。
- `parser_trace`：记录 Docling、OCR fallback、legacy parser 成功或失败。
- `error_message`：解析失败时保留失败原因。

## 持久化设计

新增 `KnowledgeObjectRepository` 作为 compiler 输出到 PostgreSQL 的边界：

- `SourceAsset` 使用 `db_id + file_id/source_uri` 生成稳定资产 ID。
- `DocumentVersion` 每次编译生成递增 `version_index`。
- `DocumentNode` 与 `EvidenceAnchor` 使用版本内稳定 key 派生 ID。
- 失败编译也会保存 `DocumentVersion(status=failed)`，但不生成节点和证据。

## 旧链路兼容

`KnowledgeBase.parse_file()` 现在先调用 compiler，再写入四类知识对象，最后仍把 Markdown 保存到 `kb-parsed` 并更新 `markdown_file`。

## 清理设计

清理分三层：

- 活跃数据：只改 PoE seed 文案，不删 seed 文件。
- 当前 context-cache：把旧品牌字面量改为 legacy 描述。
- 历史 archive：删除旧身份、旧演示身份或乱码的 Markdown，更新索引。
