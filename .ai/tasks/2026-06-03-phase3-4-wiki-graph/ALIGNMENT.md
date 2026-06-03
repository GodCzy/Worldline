# Phase 3/4 Alignment

更新时间：2026-06-03

## 目标

完成 Phase 3 LLM Wiki Mainline 和 Phase 4 Temporal Evidence Graph。

## Phase 3 验收

- Wiki 页面包含 STORM 风格 outline、章节、引用、争议点和待验证问题。
- `WikiPage` 包含人工审核状态、freshness、backlinks、evidence coverage。
- RAG 只作为 evidence candidate recall，不作为主信息架构。
- 页面输出仍兼容现有 `/wiki/pages` 和 `/wiki/pages/{page_id}` 接口。

## Phase 4 验收

- 实体、关系和时间事实都有 evidence ids。
- 图谱 metadata 包含 Graphiti 风格 episode、provenance、validity window。
- timeline 支持 temporal fact conflict detection。
- 提供 Neo4j projection，只读导出，不直接写外部图数据库。

## 不做范围

- 不新增数据库 schema。
- 不启用外部 Neo4j 写入。
- 不把 KAG/HippoRAG 作为生产迁移目标。
- 不改前端 Phase 5 工作台。

