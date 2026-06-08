# Worldline Agent Instructions

更新时间：2026-06-08

## 项目身份

Worldline 是 Joy 重新开发中的 Evidence-backed LLM Wiki + Temporal Knowledge Graph OS 项目，目标是把文档、网页、代码、证据、Wiki、图谱、时间变化、MCP 工具、Agent 工作流和评估回放编译为可浏览、可验证、可推理、可被外部 Agent 调用的知识工作台。

本项目不是普通 RAG 聊天页，也不是旧演示项目的延续。

RAG 只作为证据回查、长尾召回和候选上下文补充层；LLM Wiki、Evidence Graph、时间事实和质量门禁是主产品形态。

## 活跃路径

- 活跃工程根目录：`D:\dev\Worldline`
- 旧设计目录：`D:\document\Worldline`，只作为指针，不作为当前事实源。
- 总结输出目录：`D:\document\OutputMD`

## 当前事实源

- `README.md`：启动、验证、目录边界。
- `AGENTS.md`：项目级 Agent 规则。
- `docs/index.md`：当前最小文档站。
- `.ai/tasks/2026-06-03-worldline-reset/`：本次重启任务、证据和决策。
- `.ai/tasks/2026-06-03-worldline-frontier-stack/`：前沿技术栈、项目书和重构路线证据。
- `.ai/tasks/2026-06-08-product-planning-upgrade/ROADMAP.md`：P3 后续产品/工程路线图。
- `.ai/tasks/2026-06-08-project-operating-plan-worktree-cleanup/`：项目执行工作流、子代理/MCP/skill 使用和工作树清理证据。
- `docs/product/worldline-project-book.md`：当前项目书。
- `docs/product/worldline-next-roadmap.md`：长期后续路线图。
- `docs/architecture/agent-operating-workflow.md`：Agent 工作流、子代理分工、工具治理和提交规则。
- `docs/architecture/`：知识编译链、UI、MCP/Skill 治理和评估门禁。

旧 `.ai/tasks`、`docs/archive`、`docs/context-cache`、`PROJECT_BOOK.md`、`WORLDLINE_PROJECT_PLAN.md`、`CODEX_WORKFLOW.md`、旧 artifacts 和旧主题 demo 数据均不再作为事实源。

## 工程边界

- 清理阶段不改变后端 API、数据库 schema、MCP tool contract 或前端路由 contract。
- 保留 `server/`、`src/`、`web/`、`test/`、`docker/`、`scripts/` 的现有工程边界。
- 不把大型依赖、`node_modules`、Python venv、模型权重、Milvus/Neo4j/Postgres 数据目录放入仓库或 `D:\document\Worldline`。
- 不把密钥、Token、账号、付费信息或个人凭据写入仓库、Markdown 或 Agent 指令文件。

## 重构规则

- 先读现有代码和测试，再修改。
- 优先沿用 FastAPI、ARQ、Redis、Postgres、MinIO、Milvus、Neo4j、Vue 3、Vite、Pinia、Ant Design Vue、LangGraph 和 MCP 的现有方向。
- 不整体迁移到 RAGFlow、KAG、Graphiti、DeepWiki、Dify、Qdrant 或 pgvector，除非后续有明确评估收益。
- STORM、Graphiti、GraphRAG、KAG、HippoRAG、Cognee、mem0、Letta 等项目只按当前文档中的保留/借鉴/实验/暂缓边界使用。
- 第一阶段 Worldline UI 先用 Vue + SVG/Canvas + G6 做黑底青金发光世界线，不默认引入 Three.js/TresJS/Cosmograph。
- 多 Agent 协作时，一个主控 Agent 决策和改文件，其他 Agent 只做研究、审查或测试报告。
- P3 执行先读 `docs/product/worldline-next-roadmap.md` 和 `docs/architecture/agent-operating-workflow.md`，再为具体切片创建独立 `.ai/tasks/<YYYY-MM-DD-p3-x>/`。
- 后续提交必须按逻辑包显式 stage，检查 `git diff --cached --name-status` 和 `git diff --cached --check`，不要在脏工作树上直接 `git add .`。

## 验证要求

清理或重构后至少运行：

```powershell
rg --files -g '*.md' D:\dev\Worldline
rg --files -g '*.md' D:\document\Worldline
docker compose config
pnpm --dir web build
npm run docs:build
```

涉及后端或模型契约时补充：

```powershell
uv run --group test pytest test\test_knowledge_object_models.py test\test_worldline_live_services.py test\test_evidence_service.py
```

## 汇报要求

任务结束时说明：

- 实际删除或重建了什么。
- 修改/创建了哪些关键文件。
- 做过哪些验证。
- 仍有什么风险或后续需要 Joy 手动处理。
- `D:\document\OutputMD\...` 总结路径。
