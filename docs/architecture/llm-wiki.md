# LLM Wiki Architecture

更新时间：2026-06-03

## Intent

Worldline 的 Wiki 是主阅读面，不是 RAG 结果缓存。Wiki 页面必须能说明哪些 claim 有证据、哪些问题还需要人工验证。

## Phase 3 Implementation

- `AutoWikiService` 从 evidence-bound chunks 构建页面。
- 页面 metadata 包含 STORM-lite outline、sections、claims、citations、disputes、open questions、review、evidence coverage。
- `WikiRepository` 在响应顶层暴露这些字段，同时保留 `metadata` 兼容扩展。
- `freshness` 继续记录 source chunk ids、doc version ids 和 evidence count。
- `backlinks` 建立 home、document、topic、glossary 之间的可导航关系。

## RAG Role

RAG 只作为 evidence candidate recall：

- 补充候选 chunk；
- 帮助召回长尾证据；
- 支持质量门禁覆盖率；
- 不定义 Wiki 页面结构；
- 不替代人工 review 和 evidence coverage。

## Review Contract

每个页面应至少提供：

- `review.status`
- `evidence_coverage.status`
- `outline.style`
- `claims[].evidence_ids`
- `citations[].evidence_id`
- `open_questions[]`
- `disputes[]`

