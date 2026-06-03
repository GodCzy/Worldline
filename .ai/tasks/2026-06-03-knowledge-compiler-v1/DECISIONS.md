# Knowledge Compiler v1 Decisions

更新时间：2026-06-03

## Decisions

- Phase 2 不改数据库 schema；line span 写入 EvidenceAnchor，同时在 DocumentNode metadata 保留一份只读 trace。
- Docling reading order 优先使用 `iterate_items()`，因为它比单独遍历 texts/tables/pictures 更接近原文顺序。
- 图片节点优先用 `image_ref` 定位 char span，因为 caption 可能来自视觉对象而不出现在 Markdown。
- 每次编译都产生新的 DocumentVersion，不在 Phase 2 做版本去重；去重和 retention 留给后续运维策略。
- 新增 API 只读，不给外部 Agent 提供数据库直写能力。

## Tradeoffs

- 未新增 DocumentNode line_start/line_end 数据库列，避免 schema churn；如果后续 UI 需要高频查询节点 line span，再通过迁移补列。
- stats 是 JSON 扩展字段，优先保证可回放和可解释；严格 schema 可在评估门禁阶段再固化。

