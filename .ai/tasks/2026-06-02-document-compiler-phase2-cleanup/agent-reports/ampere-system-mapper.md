# Ampere System Mapper Summary

- 第二阶段落点应沿现有 knowledge 模块，不另起孤立入口。
- 关键路径：`server/routers/knowledge_router.py`、`src/knowledge/base.py`、`src/knowledge/indexing.py`、`src/storage/postgres/models_knowledge.py`。
- 现有 Docling 只输出 Markdown，缺少 AST、EvidenceAnchor 和 repository/service 写入链路。
- 建议新增 compiler service 和 knowledge object repository，小改 `parse_file()`。
