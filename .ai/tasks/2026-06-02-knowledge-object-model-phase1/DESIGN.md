# Design

更新时间：2026-06-02

## 模型关系

`SourceAsset` 是原始来源对象，覆盖文件、网页、代码仓库、API 和外部 MCP 数据源。

`DocumentVersion` 表示某个 `SourceAsset` 的一次文档编译版本，并通过可空 `file_id` 兼容现有 `KnowledgeFile`。

`DocumentNode` 表示 Document AST 节点，保留父子结构、顺序、页面、bbox、表格、图片和文本范围。

`EvidenceAnchor` 绑定具体 `DocumentVersion` 与 `DocumentNode`，为后续 chunk、实体、关系、Wiki 段落和回答 claim 提供证据来源。

## Schema 策略

本阶段沿用仓库现有 SQLAlchemy `create_all` 与兼容 `ALTER TABLE IF EXISTS` 风格。`ensure_knowledge_schema()` 先补建知识层表，再执行已有兼容字段升级语句。

## 兼容性

旧 `KnowledgeFile` 继续表示知识库文件管理记录。新 `SourceAsset` 不替代旧表，先通过 `DocumentVersion.file_id` 建立桥接，降低对现有上传和解析链路的影响。
