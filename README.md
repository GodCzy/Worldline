# Worldline

Worldline 是一个 **Evidence-backed LLM Wiki + Temporal Knowledge Graph OS**：把文档、网页、代码、证据、Wiki 页面、时间事实、知识图谱关系、质量门禁、MCP 工具和 Agent 运行历史，组织成可阅读、可引用、可审查、可回放的知识工作台。

它不是普通 RAG 聊天页。RAG 在 Worldline 中只是辅助召回层；核心产品形态是有证据来源的 LLM Wiki、时间知识图谱、可分支的 Worldline 画布、可回放的 Agent 运行账本，以及受控的外部工具接入。

## 当前状态

当前本地开发范围已经完成到 P5。

| 模块 | 状态 | 说明 |
|---|---|---|
| 基线知识工作台 | 基本完成 | 知识库创建、主题闭环、Dashboard QA、上传/解析/查询链路和全站 UI QA 已完成。内容知识库和第一版图谱后端是可继续扩展的基线。 |
| P3 产品核心 | 已完成 | Evidence-backed LLM Wiki、时间图谱、分支画布、Agent Run Ledger/Replay、MCP 治理、质量门禁回放和紧凑控制台 UX 已实现并验证。 |
| P4 运维硬化 | 已完成 | 失败证据、受控重试、陈旧来源重建、作用域预算、管理员观测和清理流程已实现。 |
| P5 本地公开演示 | 已完成 | 安全演示数据集、只读分支分享页、JSON/Markdown evidence bundle 导出已实现。 |
| 外部集成 | 受控待启用 | GitHub PR/Issue 集成、Firecrawl/Tavily 类采集工具需要单独授权、密钥审查和回滚方案。 |

准确的完工判断：

- 本地 P3/P4/P5 功能闭环已经完成并验证。
- 项目还不是已上线运营的生产 SaaS。正式生产部署、外部连接器授权、长期 SLO、备份恢复和真实用户运营规则仍需要单独发布流程。

最近验证检查点：

- P5 focused pytest：`9 passed, 1 warning`
- P5 Edge 桌面/移动 QA：通过
- Release gate：`12/12` 通过
- Vite 生产构建：通过
- VitePress 文档构建：通过
- `docker compose config`：通过

## 核心能力

### Evidence Ledger

Worldline 保留来源、版本、锚点和证据关系，避免把知识压平成不可追踪的文本。核心对象包括：

- `SourceAsset`
- `DocumentVersion`
- `DocumentNode`
- `EvidenceAnchor`
- `KnowledgeChunk`
- `WikiPage`
- `KnowledgeEntity`
- `KnowledgeRelationship`
- `TemporalFact`
- `QualityGateRun`

### LLM Wiki

LLM Wiki 是主要阅读界面，用于生成结构化、可引用、可审查的知识页面，并支持陈旧检测、重建流程和质量门禁。

### Temporal Knowledge Graph

时间知识图谱用于表达实体、关系、时间有效性、冲突和证据支撑，并能从 Wiki、画布和质量门禁跳转到图谱/时间线焦点。

### Worldline Branch Canvas

分支画布把一个根问题拆成多条证据支撑路径，展示 Wiki、图谱、时间线、质量门禁和收敛点之间的关系。

### Agent Run Ledger And Replay

Agent 运行会被保存为可回放的运行记录、事件、产物、门禁结果、证据引用和运行 manifest。这样 Agent 的工作过程不是一次性聊天记录，而是可以审查的工程账本。

### MCP And Skill Governance

外部 Agent 工具通过服务边界、审计日志、禁用策略、连接器审查清单和回滚步骤管理。默认不允许外部工具直接写数据库，也不默认开放无限制文件系统或管理员权限。

### Operational Health

运维健康模块覆盖队列状态、失败证据、重试、陈旧来源重建、作用域预算、清理准备度和管理员操作端点。

### Public Demo And Evidence Bundles

P5 提供确定性的只读公开演示：

- 分享页面：`/worldline/share/demo-branch-evidence`
- 数据集 API：`GET /api/worldline/public-demo/dataset`
- 分支分享 API：`GET /api/worldline/public-demo/branches/{share_id}`
- JSON 证据包：`GET /api/worldline/public-demo/evidence-bundle?share_id=demo-branch-evidence&format=json`
- Markdown 证据包：`GET /api/worldline/public-demo/evidence-bundle?share_id=demo-branch-evidence&format=markdown`

公开演示端点是只读的，不暴露实时知识库写入、管理员操作、MCP 写操作、GitHub 写操作或采集连接器。

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
- Docling / LightRAG / LlamaIndex 集成路径

前端：

- Vue 3
- Vite
- Pinia
- Ant Design Vue
- G6
- D3
- ECharts
- Graphology / Sigma

文档与验证：

- VitePress
- pytest
- Ruff
- Docker Compose
- Edge/Browser 截图 QA 脚本

## 仓库结构

```text
server/   FastAPI 应用、router、中间件
src/      领域服务、存储层、知识编译、Agent、MCP、配置
web/      Vue 3 前端
test/     pytest 测试
docs/     当前产品和架构文档
scripts/  迁移、发布门禁、QA、smoke 脚本
docker/   Dockerfile 和容器支持文件
.ai/      任务证据、截图、决策、验证报告
```

## 环境要求

推荐本地环境：

- Docker Desktop 或兼容 Docker Engine
- Docker Compose v2
- Python `>=3.12,<3.14`
- `uv`
- Node.js 与 `pnpm`
- Git

按需准备：

- GPU 和模型资产：用于完整 MinerU/PaddleX OCR profile。
- 模型、搜索或采集服务 API Key：只在启用真实外部集成时需要。
- GitHub 授权：只在启用 PR/Issue 集成时需要。

不要提交密钥。API Key、Token、数据库密码和管理员密码应放在 `.env` 或密钥管理器中，不能写入公开 README、issue、PR、截图或仓库文档。

## Docker Compose 快速启动

克隆仓库：

```bash
git clone https://github.com/GodCzy/Worldline.git
cd Worldline
```

创建本地环境配置：

```bash
cp .env.template .env
```

如需模型供应商、搜索服务或非默认服务配置，先编辑 `.env`。启动前可以检查 compose 配置：

```bash
docker compose config
```

启动默认开发栈：

```bash
docker compose up -d
```

默认访问地址：

| 服务 | 地址 |
|---|---|
| 前端 | `http://127.0.0.1:5173` |
| API | `http://127.0.0.1:5050` |
| API health | `http://127.0.0.1:5050/api/system/health` |
| Neo4j Browser | `http://127.0.0.1:7474` |
| MinIO Console | `http://127.0.0.1:9001` |

如果数据库为空，首次进入系统会走管理员初始化流程。仓库不提供固定默认管理员密码，密码必须由部署者在首次初始化或本地脚本中设置。

停止服务：

```bash
docker compose down
```

只有在确认资源和 GPU 要求后，再启动可选 OCR/模型服务：

```bash
docker compose --profile all up -d
```

## 管理员初始化

Worldline 有两种初始化超级管理员的方式。

方式一：首次运行页面或 API 初始化。

1. 启动后打开 `http://127.0.0.1:5173`。
2. 如果数据库为空，按页面提示创建初始超级管理员。
3. 登录 ID 只支持字母、数字、下划线，长度 3-20。
4. 初始化后会创建角色为 `superadmin` 的超级管理员。

也可以直接调用 API：

```bash
curl -X POST http://127.0.0.1:5050/api/auth/initialize \
  -H "Content-Type: application/json" \
  -d '{"user_id":"admin","password":"<your-strong-password>"}'
```

方式二：用脚本创建或重置本地超级管理员。

```bash
export POSTGRES_URL="postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/worldline_know"
export WORLDLINE_SUPER_ADMIN_NAME="admin"
export WORLDLINE_SUPER_ADMIN_USER_ID="admin"
export WORLDLINE_SUPER_ADMIN_PASSWORD="<your-strong-password>"
uv run python scripts/ensure_superadmin.py
unset WORLDLINE_SUPER_ADMIN_PASSWORD
```

Windows PowerShell：

```powershell
$env:POSTGRES_URL = "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/worldline_know"
$env:WORLDLINE_SUPER_ADMIN_NAME = "admin"
$env:WORLDLINE_SUPER_ADMIN_USER_ID = "admin"
$env:WORLDLINE_SUPER_ADMIN_PASSWORD = "<your-strong-password>"
uv run python scripts/ensure_superadmin.py
Remove-Item Env:\WORLDLINE_SUPER_ADMIN_PASSWORD
```

登录接口：

```bash
curl -X POST http://127.0.0.1:5050/api/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=<your-strong-password>"
```

## 本地开发

安装后端依赖：

```bash
uv sync --all-groups
```

安装前端依赖：

```bash
pnpm --dir web install
```

前端连接本地 API：

```bash
export VITE_API_URL=http://127.0.0.1:5050
pnpm --dir web dev
```

Windows PowerShell：

```powershell
$env:VITE_API_URL = "http://127.0.0.1:5050"
pnpm --dir web dev
```

文档站本地运行：

```bash
npm run docs:dev
```

构建前端：

```bash
pnpm --dir web build
```

构建文档：

```bash
npm run docs:build
```

## 常用验证命令

通用检查：

```bash
docker compose config
pnpm --dir web build
npm run docs:build
```

后端重点检查：

```bash
uv run --group test pytest test/test_worldline_public_demo_service.py test/test_worldline_phase6_7_release_gate.py -s
uv run --group test pytest test/test_worldline_operational_health_service.py test/test_worldline_phase6_7_release_gate.py -s
```

Ruff 示例：

```bash
uv run --group dev ruff check src/services/worldline_public_demo_service.py src/services/worldline_release_gate_service.py
```

发布门禁：

```bash
uv run python scripts/worldline_phase6_7_release_gate.py --output .ai/tasks/release-gate-report.json
```

如果在 WSL 中运行，并且 Codex skills 位于 Windows 用户目录，可以显式传入 skills 根目录：

```bash
uv run python scripts/worldline_phase6_7_release_gate.py \
  --codex-skills-root /mnt/c/Users/Joy/.codex/skills \
  --output .ai/tasks/release-gate-report.json
```

## Public Demo 流程

启动服务后打开：

```text
http://127.0.0.1:5173/worldline/share/demo-branch-evidence
```

页面展示：

- 确定性的公开演示数据集；
- 只读 Worldline 分支；
- evidence、wiki、graph、timeline 和 gate 引用；
- JSON 和 Markdown evidence bundle 导出；
- replay 与 rollback 信息。

该路由只适合受控演示，不用于开放实时管理权限或写权限。

## GitHub Pages 文档部署

仓库包含 VitePress 文档站和 GitHub Actions workflow。如果 Pages workflow 报错类似 “获取 Pages 站点失败” 或 `HttpError: Not Found`，通常不是 README 提交失败，而是 GitHub Pages 未启用。

处理方式：

1. 打开 GitHub 仓库 `Settings`。
2. 进入 `Pages`。
3. 在 `Build and deployment` 中把 Source 设置为 `GitHub Actions`。
4. 回到 `Actions` 重新运行部署 workflow。

本地验证文档站：

```bash
npm run docs:build
```

## 安全与集成边界

Worldline 把外部工具视为受控集成：

- GitHub PR/Issue 工作流需要明确授权和回滚路径。
- Firecrawl/Tavily 类采集工具需要做来源审查、数据暴露审查和密钥处理审查。
- MCP server 与 tool 通过 allowlist、禁用策略和审计日志治理。
- 外部 Agent 应通过 Worldline 服务接口写入，不应直接写数据库。
- 密钥、Token、管理员密码不能写进仓库、公开 Markdown、截图、issue、PR 或公开 URL。

## 当前文档

- 产品状态：`docs/product/worldline-completion-matrix.md`
- 公开演示：`docs/product/public-demo.md`
- 项目书：`docs/product/worldline-project-book.md`
- 路线图：`docs/product/worldline-next-roadmap.md`
- 知识编译器：`docs/architecture/knowledge-compiler.md`
- LLM Wiki：`docs/architecture/llm-wiki.md`
- 时间证据图谱：`docs/architecture/temporal-evidence-graph.md`
- Worldline UI：`docs/architecture/worldline-ui.md`
- Agent 工作流：`docs/architecture/agent-operating-workflow.md`
- MCP 与 Skill 治理：`docs/architecture/mcp-skill-governance.md`
- 运维硬化：`docs/architecture/operational-hardening.md`
- 评估门禁：`docs/architecture/evaluation-gates.md`

## License

See `LICENSE`.
