# Phase 3/4 Decisions

更新时间：2026-06-03

## Decisions

- Phase 3 不直接接入外部 STORM 项目；采用 STORM-lite 数据结构和 deterministic renderer，先保证本地可测和 evidence-bound。
- Wiki 人工审核状态放入 `WikiPage.metadata.review`，不新增列，避免 schema churn。
- RAG 不生成最终 Wiki 结构，只记录为 `rag_role = evidence_candidate_recall`。
- Phase 4 不直接写外部 Neo4j；提供 projection contract，后续在权限和环境齐备后再接同步任务。
- TemporalFact conflict detection 先按 subject、predicate、occurred_at 聚合，发现同时间同谓词不同 object 即标记人工审核。

## Tradeoffs

- 现阶段 deterministic extraction 不能替代 LLM/STORM 多代理深度写作，但它让证据、引用、审核和图谱边界先稳定。
- validity window 主要来自文档版本和日期 mention，后续可引入来源发布时间、失效时间和事实撤销事件。

