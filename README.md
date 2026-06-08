# Worldline

更新时间：2026-06-08

Worldline 是 Joy 重新开发中的 Evidence-backed LLM Wiki + Temporal Knowledge Graph OS 工程。当前事实源从本文件、项目级 `AGENTS.md`、`docs/index.md`、`.ai/tasks/2026-06-03-worldline-reset/` 和 `.ai/tasks/2026-06-03-worldline-frontier-stack/` 重新开始；旧阶段规划、旧归档、旧演示主题和旧 QA 证据不再作为项目依据。

## 当前根目录

- 活跃工程：`D:\dev\Worldline`
- 旧设计归档指针：`D:\document\Worldline`
- 任务总结输出：`D:\document\OutputMD`

## 当前定位

- 主线：Evidence-backed LLM Wiki + Temporal Knowledge Graph OS。
- LLM Wiki、Evidence Graph、时间事实和质量门禁是核心资产。
- RAG 只作为证据回查、长尾召回和候选上下文补充层。
- 不整体套壳迁移到 Dify、RAGFlow、KAG、Graphiti 或 DeepWiki。

## 保留边界

- 保留核心代码、测试、Docker、锁文件、环境模板和 `LICENSE`。
- 保留现有后端 API、数据库 schema、MCP tool contract 和前端路由 contract。
- 清理旧 Markdown 规划、旧 `.ai/tasks`、旧 `.codex` 多 Agent 配置、旧 artifacts 和旧演示残留。

## 目录结构

- `server/`：FastAPI 入口、router 和中间件。
- `src/`：领域服务、存储、知识处理、Agent、MCP 和配置。
- `web/`：Vue 3、Vite、Pinia、Ant Design Vue 前端。
- `test/`：pytest 测试。
- `docker/`：容器启动与镜像脚本。
- `scripts/`：迁移、QA、smoke 脚本。
- `docs/`：当前最小文档站，只记录新事实源。

## 当前文档

- `docs/product/worldline-project-book.md`：新项目书。
- `docs/product/worldline-next-roadmap.md`：P3 及后续产品/工程路线图。
- `docs/architecture/knowledge-compiler.md`：知识编译链。
- `docs/architecture/worldline-ui.md`：世界线工作台 UI。
- `docs/architecture/agent-operating-workflow.md`：主控 Agent、子代理、skills、MCP、Browser/GitHub 和提交工作流。
- `docs/architecture/mcp-skill-governance.md`：MCP 与 skill 治理。
- `docs/architecture/evaluation-gates.md`：评估门禁。

## 下一阶段启动

P3 默认从 Evidence-backed LLM Wiki 垂直切片开始：

```text
请读取 D:\dev\Worldline\docs\product\worldline-next-roadmap.md 和 D:\dev\Worldline\docs\architecture\agent-operating-workflow.md，并从 D:\dev\Worldline 继续。先做 P3-1 Evidence-backed LLM Wiki：单个真实内容知识库生成可阅读、可引用、可审查的 Wiki 页面，并完成 focused pytest 与桌面/390px 截图 QA。
```

## 启动与验证

```powershell
Copy-Item .env.template .env
docker compose config
docker compose up -d
$env:VITE_API_URL = "http://127.0.0.1:5050"
pnpm --dir web dev
```

```powershell
uv run --group test pytest test\test_knowledge_object_models.py test\test_worldline_live_services.py test\test_evidence_service.py
pnpm --dir web build
npm run docs:build
```

## 重构原则

- 先恢复清晰工程事实，再做功能升级和模块重构。
- 不把 Worldline 降级成普通 RAG 聊天页。
- 外部 Agent 不直接写数据库，必须通过受控接口和审计边界。
- 新规划只写入新的 `.ai/tasks` 任务目录，不引用旧阶段文档。
