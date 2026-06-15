# Worldline

Worldline 是一个 **证据驱动的 LLM Wiki 与时间知识图谱工作台**。它把文档、网页、代码、知识片段、引用证据、时间事实、图谱关系和 Agent 运行记录组织成可阅读、可追溯、可审查的知识系统。

Worldline 不是普通 RAG 聊天页面。RAG 只负责辅助召回；核心是可引用的 Wiki 页面、证据链、时间知识图谱、分支化分析画布和可回放的 Agent 工作流。

## 核心能力

- **Evidence-backed Wiki**：生成带来源、锚点和版本信息的知识页面。
- **Temporal Knowledge Graph**：表达实体、关系、时间有效性和冲突证据。
- **Worldline Branch Canvas**：把一个问题拆成多条证据支撑的分析分支。
- **Agent Run Ledger**：记录 Agent 运行过程、产物、门禁结果和回放信息。
- **Quality Gates**：对知识构建、演示数据和发布流程进行可复验检查。
- **Public Demo Bundle**：提供只读公开演示数据和 JSON/Markdown 证据包导出。

## 项目状态

当前仓库提供可本地运行的开发与演示版本：

- 知识库、Wiki、图谱、分支画布、Agent 账本和公开演示链路已形成闭环。
- Public Demo 是只读的，不暴露后台写入、管理操作或外部连接器写权限。
- 生产部署、外部连接器授权、长期备份恢复和真实用户运营策略需要单独配置。

## 技术栈

后端：

- FastAPI
- SQLAlchemy async
- PostgreSQL
- Redis / ARQ
- MinIO
- Milvus
- Neo4j
- LangGraph
- MCP

前端：

- Vue 3
- Vite
- Pinia
- Ant Design Vue
- G6 / D3 / ECharts / Sigma

文档与验证：

- VitePress
- pytest
- Ruff
- Docker Compose

## 目录结构

```text
server/   FastAPI 应用、路由和中间件
src/      领域服务、存储层、知识编译、Agent、MCP、配置
web/      Vue 3 前端
test/     pytest 测试
docs/     产品与架构文档
scripts/  迁移、验证、发布门禁和辅助脚本
docker/   Dockerfile 与容器配置
```

## 快速启动

环境要求：

- Docker Desktop 或兼容 Docker Engine
- Docker Compose v2
- Git

启动：

```bash
git clone https://github.com/GodCzy/Worldline.git
cd Worldline
cp .env.template .env
docker compose up -d
```

默认地址：

| 服务 | 地址 |
|---|---|
| Web | `http://127.0.0.1:5173` |
| API | `http://127.0.0.1:5050` |
| API Health | `http://127.0.0.1:5050/api/system/health` |
| Neo4j Browser | `http://127.0.0.1:7474` |
| MinIO Console | `http://127.0.0.1:9001` |

停止：

```bash
docker compose down
```

## 本地开发

后端依赖：

```bash
uv sync --all-groups
```

前端依赖与开发服务：

```bash
pnpm --dir web install
pnpm --dir web dev
```

常用检查：

```bash
docker compose config
pnpm --dir web build
npm run docs:build
```

## 演示入口

只读公开演示：

```text
http://127.0.0.1:5173/worldline/share/demo-branch-evidence
```

公开演示 API：

```text
GET /api/worldline/public-demo/dataset
GET /api/worldline/public-demo/branches/{share_id}
GET /api/worldline/public-demo/evidence-bundle?share_id=demo-branch-evidence&format=json
GET /api/worldline/public-demo/evidence-bundle?share_id=demo-branch-evidence&format=markdown
```

## 文档

- `docs/product/worldline-project-book.md`
- `docs/product/worldline-next-roadmap.md`
- `docs/product/public-demo.md`
- `docs/architecture/knowledge-compiler.md`
- `docs/architecture/llm-wiki.md`
- `docs/architecture/temporal-evidence-graph.md`
- `docs/architecture/worldline-ui.md`
- `docs/architecture/mcp-skill-governance.md`

## 安全说明

- 不要提交 `.env`、API Key、Token、数据库密码或管理员密码。
- 外部连接器默认不是公开写入口，启用前需要审查权限范围和回滚路径。
- Public Demo 路由只读，不用于授予实时管理权限。

## License

See `LICENSE`.
