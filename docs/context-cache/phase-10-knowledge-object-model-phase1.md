# Phase 10 Knowledge Object Model Phase 1

更新时间：2026-06-02

## 当前阶段

Phase 10：database and knowledge data-chain standardization。

本次第一阶段只落地统一知识对象模型与 EvidenceAnchor 底座，不接入 Docling、chunking、Milvus、Neo4j、Auto-Wiki、MCP Server 或前端 UI。

## 已落地模型

新增 SQLAlchemy 模型位于 `src/storage/postgres/models_knowledge.py`：

- `SourceAsset`
  - 原始来源对象。
  - 覆盖文件、网页、代码仓库、API、外部 MCP 数据源等。
  - 可选关联 `knowledge_bases.db_id`。
- `DocumentVersion`
  - 某个 `SourceAsset` 的一次文档编译版本。
  - 可选关联现有 `knowledge_files.file_id`，用于兼容旧文件管理记录。
- `DocumentNode`
  - Document AST 节点。
  - 支持父子结构、节点顺序、表格、图片、页面、bbox 和 metadata。
- `EvidenceAnchor`
  - 可追溯证据锚点。
  - 通过 `doc_version_id` 和 `node_id` 绑定具体文档版本与 AST 节点。

## 数据库兼容策略

`src/storage/postgres/manager.py` 的 `ensure_knowledge_schema()` 现在会先执行 `KnowledgeBase.metadata.create_all`。

原因：

- 新库可以补建所有知识层表。
- 旧库仍继续使用原有 `ALTER TABLE IF EXISTS ... ADD COLUMN IF NOT EXISTS ...` 兼容字段升级。
- 不引入 Alembic，保持当前仓库既有 schema 管理方式。

## 测试基线

新增测试：

- `test/test_knowledge_object_models.py`

覆盖：

- 四个表已注册到共享 `Base.metadata`。
- 关键字段、唯一约束、外键和索引存在。
- `metadata` 数据库列通过 `asset_metadata`、`node_metadata`、`evidence_metadata` 避免 SQLAlchemy 保留属性冲突。
- 四个表可编译为 PostgreSQL DDL。

## 后续边界

第二阶段才开始处理：

- Docling 主解析。
- OCR-heavy fallback。
- AST 真实生成。
- EvidenceAnchor 从 Document AST 派生。
- chunk、实体、关系、Wiki 页面派生。
