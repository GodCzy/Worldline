# Worldline Docs

更新时间：2026-06-03

这是 Worldline 重启后的最小文档站。旧规划、旧归档、旧阶段上下文和旧 QA 证据已清理，不再作为当前事实源。

## 当前入口

- 工程根目录：`D:\dev\Worldline`
- 项目规则：`AGENTS.md`
- 启动与验证：`README.md`
- 重启任务证据：`.ai/tasks/2026-06-03-worldline-reset/`
- 前沿技术栈任务：`.ai/tasks/2026-06-03-worldline-frontier-stack/`
- 新项目书：`docs/product/worldline-project-book.md`
- 架构文档：`docs/architecture/`

## 当前工程形态

- Backend：FastAPI router、领域 service、repository、Postgres/MinIO/Milvus/Neo4j 相关存储层。
- Frontend：Vue 3、Vite、Pinia、Ant Design Vue。
- Agent/MCP：LangGraph 工作流和受控 MCP 工具边界。
- Validation：pytest、Vite build、VitePress build、Docker Compose config。

## 新定位

Worldline 当前主线是 Evidence-backed LLM Wiki + Temporal Knowledge Graph OS。LLM Wiki、Evidence Graph、时间事实和质量门禁是核心资产；RAG 只作为证据回查、长尾召回和候选上下文补充层。

## 当前文档

- [Worldline Project Book](./product/worldline-project-book.md)
- [Worldline Next Roadmap](./product/worldline-next-roadmap.md)
- [Knowledge Compiler Architecture](./architecture/knowledge-compiler.md)
- [LLM Wiki Architecture](./architecture/llm-wiki.md)
- [Temporal Evidence Graph Architecture](./architecture/temporal-evidence-graph.md)
- [Worldline UI Architecture](./architecture/worldline-ui.md)
- [Agent Operating Workflow](./architecture/agent-operating-workflow.md)
- [MCP And Skill Governance](./architecture/mcp-skill-governance.md)
- [Codex Plugin Inventory For Worldline](./architecture/codex-plugin-inventory.md)
- [Evaluation Gates](./architecture/evaluation-gates.md)
- [Worldline Completion Matrix](./product/worldline-completion-matrix.md)
- [Public Demo](./product/public-demo.md)

## 下一阶段

1. 先建立新的产品和架构事实。
2. 再按功能域拆解后端、前端、MCP、评估和数据流。
3. 每次重构都写入新的 `.ai/tasks/<date-task>/`，并保留验证证据。
