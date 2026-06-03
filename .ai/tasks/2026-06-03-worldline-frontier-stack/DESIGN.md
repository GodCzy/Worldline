# Worldline Frontier Stack Design

更新时间：2026-06-03

## Core Architecture

```text
Source / Parse
  -> Evidence Ledger
  -> LLM Wiki
  -> Temporal Evidence Graph
  -> Retrieval / Reasoning
  -> Agent Workflow
  -> Worldline UI
  -> Quality Gate
```

## Layers

- Source / Parse：文件、网页、仓库、笔记和多媒体进入 `SourceAsset`；Docling 产出结构化 `DocumentVersion` 和 `DocumentNode`。
- Evidence Ledger：每个可引用片段落到 `EvidenceAnchor`，保留 source uri、page、line、bbox、hash、confidence。
- LLM Wiki：STORM 风格多视角 outline、页面、backlinks、staleness 和引用包；Wiki 是主要阅读面。
- Temporal Evidence Graph：实体、关系、事件、时间有效期和 provenance；借鉴 Graphiti 的 episode/temporal model。
- Retrieval / Reasoning：Milvus/LightRAG/LlamaIndex 辅助召回，Neo4j 图遍历辅助推理，KAG/HippoRAG 作为评估实验。
- Agent Workflow：LangGraph 编排研究、抽取、合成、审查、回放和 human-in-the-loop。
- Worldline UI：黑底青金发光世界线、证据轨、时间 scrubber、图谱聚焦、Agent handoff。
- Quality Gate：引用覆盖率、图谱一致性、幻觉检查、成本/延迟、MCP 权限审计。

## Compatibility

- 保持 `/api/knowledge/databases/{db_id}/worldline/overview` 与 `/worldline/generate` 可兼容前端 hydrate。
- `/worldline/generate` 可选扩展字段：`knowledgeMode`、`layers`、`branches[].wikiRefs`、`branches[].entityRefs`、`branches[].timelineRefs`、`snapshots`、`quality`。
- 现有 MCP 工具只扩展不破坏：manifest、workflow、wiki、graph、quality gate 都继续通过 service boundary。

## UI Direction

第一阶段不用 Three.js。先用现有 Vue + SVG/Canvas + G6：

- `/worldline` 是控制台，不做营销 landing。
- `/worldline/:themeId` 是主工作台，世界线从左到右分叉汇聚。
- 证据轨随节点选择联动，显示 source/page/line/bbox。
- 时间 scrubber 展示证据新增、Wiki 重建、图谱更新、质量门运行。
- 大图谱性能达到万级节点时再启用 Sigma；沉浸式 3D 作为 v2。
