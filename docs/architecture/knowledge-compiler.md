# Knowledge Compiler Architecture

更新时间：2026-06-03

## Intent

Knowledge Compiler 把来源编译为可验证知识对象，而不是把文本直接切块塞进 RAG。

## Pipeline

```text
SourceAsset
  -> DocumentVersion
  -> DocumentNode
  -> EvidenceAnchor
  -> KnowledgeChunk
  -> WikiPage
  -> KnowledgeEntity / KnowledgeRelationship / TemporalFact
  -> QualityGateRun
```

## Rules

- Docling 是主解析入口，保留结构化 block、table、figure、heading、page span 和 reading order。
- Markdown 只是导出和阅读格式，不是唯一中间表示。
- 每个 chunk、Wiki 段落、实体、关系、时间事实都应能绑定 evidence ids。
- 解析失败、OCR fallback、模型抽取失败都必须记录错误和重试证据。
- Source hash、parser version、parse config、stats 是可回放必需字段。

## Retrieval Role

RAG 只做：

- evidence candidate recall；
- long-tail query fallback；
- Wiki/Graph 生成时的上下文补充；
- 质量门禁中的覆盖率和失败回放。

RAG 不负责定义 Worldline 的信息架构、主界面或可信度。
