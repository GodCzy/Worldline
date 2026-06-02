# Ampere Backend Interface Audit

更新时间：2026-06-02

Ampere 只读审计结论：

- Phase 2 已写入 `DocumentVersion`、`DocumentNode`、`EvidenceAnchor`。
- 缺口是 Evidence 读取接口与查询结果证据化包装。
- 建议保留旧 `/query`，新增 traced/evidence 查询接口。
- 建议新增服务层格式化 `retrieved_chunks`、`citations`、`claims`、`route_trace`。
- 风险是当前 chunk 未绑定 `evidence_ids` 时只能 best-effort 追溯。

采纳情况：

- 已新增 `KnowledgeChunk` 持久绑定。
- 已新增 `/query-evidence`，保留旧 `/query`。
- 已新增 `EvidenceQueryService`。
