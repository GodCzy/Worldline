# Worldline Frontier Stack Decisions

更新时间：2026-06-03

## Decisions

1. Worldline 的主线是 Evidence-backed LLM Wiki + Temporal Knowledge Graph OS。
2. RAG 降级为辅助召回层，不作为主产品形态。
3. 保留现有 FastAPI、Postgres、MinIO、Milvus、Neo4j、LangGraph、MCP、Docling、LightRAG、Vue/Vite/Pinia/G6/Sigma。
4. STORM 和 Graphiti 作为新增重点借鉴方向；KAG、HippoRAG、Cognee 先作为实验和架构参考。
5. 不整体迁移到 Dify、RAGFlow、KAG、Graphiti、DeepWiki、Qdrant 或 pgvector。
6. 第一阶段 UI 不引入 Three.js/TresJS/Cosmograph；先用现有 Vue + SVG/Canvas + G6。
7. 外部 Agent 不直写数据库，所有写入必须经过 Worldline service boundary 和审计日志。
8. 本地 Codex skills 独立于 Worldline 应用内 skills 管理系统，默认放 `C:\Users\Joy\.codex\skills\worldline-*`。

## Deferred

- Firecrawl、Context7、Tavily 等外部 MCP 只在密钥、权限和数据外传审查后启用。
- Sigma 用于万级图谱性能需求；Three.js/TresJS 用于沉浸式 v2。
- KAG/OpenSPG、mem0、Letta 不进入当前主链路。
