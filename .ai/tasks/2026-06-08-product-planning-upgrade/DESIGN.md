# 规划设计

## 产品核心

Worldline 的核心不是 chat，而是把来源编译成可浏览、可验证、可推理、可被 Agent 调用的知识工作台。

核心链路：

```text
SourceAsset
  -> DocumentVersion
  -> DocumentNode
  -> EvidenceAnchor
  -> KnowledgeChunk
  -> WikiPage
  -> KnowledgeEntity / KnowledgeRelationship / TemporalFact
  -> QualityGateRun
  -> Worldline Branch
  -> Agent Handoff / Replay
```

## 规划结构

路线图按七条主线组织：

1. Evidence-backed LLM Wiki
2. Temporal Knowledge Graph
3. Worldline Branch Canvas
4. Agent Run Ledger
5. MCP / Skill Governance
6. Quality Gate Replay
7. Compact Console UX

每条主线都定义：

- 当前基线
- 下一阶段能力
- 后端对象或接口
- UI 落点
- 验收证据
- 风险与不做事项

## 执行方式

后续进入 P3 时优先采用垂直切片，而不是横向铺满：

1. 单文档 evidence-backed Wiki 切片。
2. Wiki -> Temporal Graph -> Branch Canvas 串联切片。
3. Branch -> Agent Run Ledger -> Replay 切片。
4. MCP Governance -> Quality Gate Release 切片。
