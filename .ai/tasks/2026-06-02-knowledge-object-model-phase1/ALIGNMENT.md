# Alignment

更新时间：2026-06-02

## 目标

落地 Worldline Phase 10 的第一阶段知识对象模型底座，使原始来源、文档编译版本、Document AST 节点和可追溯证据锚点具备 PostgreSQL 表级契约。

## 范围

- 新增 `SourceAsset`、`DocumentVersion`、`DocumentNode`、`EvidenceAnchor` SQLAlchemy 模型。
- 让现有知识库 schema ensure 流程能补建新增表。
- 增加离线模型契约测试和 context-cache 记录。

## 不做

- 不接入 Docling、OCR fallback、chunking、Milvus、Neo4j、Auto-Wiki、MCP Server 或前端 UI。
- 不重写旧上传、解析、文件管理和 LightRAG 流程。
- 不引入 Alembic 或新的数据库迁移框架。

## 验收标准

- 新模型注册到共享 `Base.metadata`。
- 关键字段、外键、唯一约束、索引和 JSONB 字段可验证。
- `ensure_knowledge_schema()` 能在 PostgreSQL 中创建新增表。
- 任务结论写入 `docs/context-cache/`。
