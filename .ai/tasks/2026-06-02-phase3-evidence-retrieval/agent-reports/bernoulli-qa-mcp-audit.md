# Bernoulli QA/MCP Audit

更新时间：2026-06-02

Bernoulli 只读审计结论：

- 第三阶段验收重点是证明 `KnowledgeChunk.evidence_ids` 绑定到 `EvidenceAnchor`。
- 检索链需要返回 `route_trace`、`retrieved_chunks`、claim/citation 结构。
- 离线单元测试应先锁定契约，再用少量 PostgreSQL/Milvus smoke 验证。
- Browser/Figma/Notion/MCP Inspector/Filesystem MCP 当前都不需要。

采纳情况：

- 已新增模型、仓储和服务测试。
- 已记录真实 PostgreSQL smoke 作为待验证项。
- 未启用额外 MCP/Skill。
