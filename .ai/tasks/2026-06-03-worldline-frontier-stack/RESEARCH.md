# Worldline Frontier Stack Research

更新时间：2026-06-03

## Positioning

Worldline 应采用“编译知识”路线：把来源先编译为可追溯证据、Wiki、图谱、时间事实和质量门禁结果，再把 RAG 作为辅助召回工具。

## Reference Matrix

| Project | 2026-06-03 stars | Decision | Worldline 用法 |
| --- | ---: | --- | --- |
| Docling | 60.9k | 保留基础 | 文档解析主入口，保留结构化 block/table/layout。 |
| mem0 | 57.5k | 暂缓主链路 | 未来个性化 Agent memory 参考，不做知识库主干。 |
| LlamaIndex | 49.9k | 保留但降级 | connector、retriever、eval glue，不定义产品形态。 |
| LightRAG | 36.1k | 保留实验 | 图+向量轻量检索 baseline。 |
| LangGraph | 33.7k | 保留 | 长任务、人审、可恢复工作流。 |
| GraphRAG | 33.4k | 借鉴方法 | community reports、local/global/drift 查询思路。 |
| Playwright MCP | 33.4k | 推荐验证工具 | 本地 UI smoke 和截图 QA。 |
| STORM / Co-STORM | 28.3k | 新增重点 | LLM Wiki outline、多视角研究、引用页面生成。 |
| Graphiti | 26.9k | 新增重点 | temporal graph、episode、provenance、增量事实更新。 |
| Cognee | 17.7k | 可选评估 | graph+vector+relational memory pipeline 参考。 |
| KAG | 8.8k | 概念借鉴 | schema-constrained extraction、logical-form reasoning。 |
| Firecrawl MCP | 6.5k | 按需启用 | 网页摄取，需密钥和权限审查。 |
| HippoRAG | 3.6k | 实验评估 | 多跳检索、PPR 线索追踪 baseline。 |

## External Sources

- https://github.com/docling-project/docling
- https://github.com/stanford-oval/storm
- https://github.com/getzep/graphiti
- https://github.com/microsoft/graphrag
- https://github.com/HKUDS/LightRAG
- https://github.com/OpenSPG/KAG
- https://github.com/OSU-NLP-Group/HippoRAG
- https://github.com/topoteretes/cognee
- https://github.com/mem0ai/mem0
- https://github.com/letta-ai/letta
- https://github.com/run-llama/llama_index
- https://github.com/langchain-ai/langgraph
- https://github.com/microsoft/playwright-mcp
- https://github.com/firecrawl/firecrawl-mcp-server
- https://github.com/atomicmemory/llm-wiki-compiler
- https://github.com/axoviq-ai/synthadoc

## Community Pain Points

Linux.do 等社区讨论主要作为需求痛点参考，不作为技术事实源：

- 复杂 PDF、表格、图纸、扫描件解析仍是 RAG 工程瓶颈。
- GraphRAG 的批处理成本、增量更新和可解释性需要谨慎控制。
- MCP 与 RAG 边界容易失控，必须限制工具权限和数据库写入。
- 用户真正需要的是可验证、可更新、可浏览的知识系统，不只是聊天回答。
