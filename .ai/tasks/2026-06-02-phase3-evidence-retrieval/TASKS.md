# Phase 3 Evidence Retrieval Tasks

更新时间：2026-06-02

| 任务 | 状态 | 验证 |
| --- | --- | --- |
| 读取阶段文档和第二阶段基线 | done | `PROJECT_BOOK.md`、phase2 context-cache |
| 复用 subagent 做接口和 QA 审计 | done | `agent-reports/` |
| 新增 `KnowledgeChunk` 模型 | done | `test_knowledge_object_models.py` |
| 扩展 `KnowledgeObjectRepository` | done | `test_knowledge_object_repository.py` |
| 接入 Milvus chunk 绑定和检索回填 | done | ruff + 单测覆盖仓储契约 |
| 新增 `EvidenceQueryService` | done | `test_evidence_service.py` |
| 新增 Evidence API endpoints | done | ruff import/route 静态检查 |
| 真实 PostgreSQL smoke | done | `KnowledgeChunk` 写入和 citation 回填通过 |
| docs build | done | `npm run docs:build` 通过 |
| 最终提交 | pending | 待运行 |
