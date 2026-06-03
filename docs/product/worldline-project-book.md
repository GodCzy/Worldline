# Worldline Project Book

更新时间：2026-06-03

## Product Thesis

Worldline 是 Evidence-backed LLM Wiki + Temporal Knowledge Graph OS。它把文档、网页、代码、证据、Wiki、图谱、时间变化、MCP 工具、Agent 工作流和评估回放编译为一个可浏览、可验证、可推理、可被外部 Agent 调用的知识工作台。

Worldline 不以普通 RAG 聊天页为第一形态。聊天只是进入知识系统的一种方式，核心资产是可追溯证据、自动 Wiki、时序图谱、质量门禁和可操作世界线。

## User Experience

- 第一眼看到的是黑底青金发光的世界线工作台，而不是聊天框。
- 用户上传或连接来源后，系统先生成证据账本、Wiki 页面、实体关系和时间事实。
- 用户提出问题时，系统展示多条可验证世界线，每条分支绑定证据、Wiki、图谱节点和下一步行动。
- 任何回答、分支、结论都必须能回到 `EvidenceAnchor`。

## Differentiation

- LLM Wiki 主导：先把知识编译成可读、可更新、可引用的 Wiki。
- Evidence Graph 主导：实体、关系、事件和时间有效期一等公民。
- RAG 辅助：向量/混合检索用于补充候选证据，不决定产品形态。
- MCP 受控：外部 Agent 只能通过审计过的工具边界写入或触发任务。
- 评估内建：质量门禁不是后处理，而是系统运行的一部分。

## Stack Decisions

- Keep：FastAPI、ARQ、Redis、Postgres、MinIO、Milvus、Neo4j、Vue 3、Vite、Pinia、Ant Design Vue、LangGraph、MCP、Docling、LightRAG、LlamaIndex。
- Add by pattern：STORM 风格 Wiki synthesis、Graphiti 风格 temporal graph、KAG 风格 schema/logical reasoning、HippoRAG 风格多跳检索评估。
- Evaluate only：Cognee、mem0、Letta、Firecrawl、Context7、Tavily。
- Avoid：Dify/RAGFlow/DeepWiki 套壳迁移、数据库直连写 MCP、默认全盘 filesystem MCP、过早 Three.js 重构。

## Milestones

1. 重启基线稳定。
2. Knowledge Compiler v1。
3. LLM Wiki 主线。
4. Temporal Evidence Graph。
5. Worldline UI 工作台。
6. Skill/MCP/Subagent 治理。
7. Evaluation + Public Demo。
