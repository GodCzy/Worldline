# Tasks

更新时间：2026-06-02

- [x] 映射现有 PostgreSQL 知识库模型、schema ensure 路径和测试约束。
- [x] 设计第一阶段四个知识对象模型和旧表兼容关系。
- [x] 在 `models_knowledge.py` 新增 `SourceAsset`、`DocumentVersion`、`DocumentNode`、`EvidenceAnchor`。
- [x] 更新 `PostgresManager.ensure_knowledge_schema()`，让新增表可由现有 schema ensure 流程创建。
- [x] 新增离线 SQLAlchemy 模型契约测试。
- [x] 写入 `docs/context-cache/phase-10-knowledge-object-model-phase1.md`。
- [x] 验证 ruff、离线测试和真实 PostgreSQL schema 创建。

## 下一阶段候选

- 接入 Docling 主解析，输出可持久化 Document AST。
- 定义 AST 到 EvidenceAnchor 的派生规则。
- 将 chunk、实体、关系和 Wiki 派生产物绑定 `evidence_id`。
