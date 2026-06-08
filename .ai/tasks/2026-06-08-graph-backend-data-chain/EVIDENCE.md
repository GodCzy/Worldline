# Evidence

日期：2026-06-08

## 初始复现与环境

- Windows PowerShell 侧没有 `docker` 命令；WSL Debian 侧 `docker` 可用。
- WSL `docker ps` 确认 `api-dev`、`graph`、`postgres`、`milvus`、`redis` 等服务运行中。
- 未登录访问 `/api/graph/list` 返回 401，提示需要登录后访问。
- Vite dev server 在端口 5173 运行。

## 临时管理员 QA

- 使用 `scripts/ensure_superadmin.py` 创建/更新本地 `codex_temp_admin` superadmin。
- 临时密码为进程内随机值，未写入仓库、`.env` 或总结文件。
- `/api/auth/token` 登录成功。
- QA 后已将 `codex_temp_admin` 标记为 `is_deleted=1`。
- 第一次清理脚本使用 timezone-aware datetime 失败；随后改用 naive UTC datetime 清理成功。

## 真实 API 探测摘要

- `/api/graph/list`：200，当前仅返回默认 `neo4j` 图谱。
- `/api/graph/neo4j/info`：200，`status=open`，`entity_count=0`，`relationship_count=0`。
- `/api/graph/subgraph?db_id=neo4j`：200，`nodes=[]`，`edges=[]`。
- `/api/graph/stats?db_id=neo4j`：200，`total_nodes=0`，`total_edges=0`。
- `/api/knowledge/databases`：200，但当前响应中没有可直接用于继续验证 Worldline graph/timeline DB endpoints 的用户知识库。

## 修复

- 修改 `server/routers/graph_router.py`：
  - `_get_graph_adapter()` 先调用 `GraphAdapterFactory.detect_graph_type(db_id, knowledge_base)`。
  - 只有 `upload` 类型需要 `_ensure_graph_base_running()`。
  - `lightrag` 类型直接创建 LightRAG adapter，并传入 `{"kb_id": db_id}`。
  - adapter 初始化失败统一转为 503，由 `/subgraph`、`/stats`、`/labels` 的既有降级分支返回 `success: true`、`degraded: true` 与可解释空数据。
- 新增 `test/test_graph_router_adapter.py`：
  - 覆盖 LightRAG 图谱不应被 Upload/Neo4j `graph_base` 启动阻塞。
  - 覆盖 LightRAG adapter 初始化失败时返回可解释降级空图谱。

## 通过的验证

### `pytest test/test_graph_router_adapter.py -q -vv`

- 运行方式：WSL Debian，仓库根目录，`.venv/bin/pytest`。
- 结果：通过。
- 摘要：`2 passed, 1 warning in 14.88s`。
- warning：SQLAlchemy `declarative_base()` deprecation warning，非本次新增行为失败。

### `pytest test/api/test_unified_graph_router.py::test_get_subgraph_lightrag -q -vv`

- 运行方式：使用本地临时 `codex_temp_admin` 注入 `TEST_USERNAME` / `TEST_PASSWORD`。
- 结果：通过。
- 摘要：`1 passed in 9.00s`。
- QA 后已将临时账号重新标记为 `is_deleted=1`。

### `git diff --check -- server/routers/graph_router.py test/test_graph_router_adapter.py .ai/tasks/2026-06-08-graph-backend-data-chain`

- 结果：通过。
- 备注：仅提示 `server/routers/graph_router.py` 工作副本的 CRLF 下次被 Git 接触时会替换为 LF。

### `wsl -d Debian --cd /mnt/d/dev/Worldline -- docker compose config --quiet`

- 结果：通过。
- 备注：使用 `--quiet` 避免输出 compose 环境细节。

### `wsl -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && command -v node && command -v npm && npm run docs:build'`

- 结果：通过。
- `node`：`/home/joy/.local/bin/node`。
- `npm`：`/home/joy/.local/bin/npm`。
- 摘要：VitePress `build complete in 35.82s`。
- 备注：此前直接通过 `wsl --cd ... -- /home/joy/.local/bin/npm run docs:build` 失败，原因是非登录 WSL 环境中 `node` 不在 PATH；登录 shell 下通过。

## 未通过或未完成的验证

### 曾经失败：`test/test_worldline_live_services.py::test_live_graph_timeline_and_stale_detector`

- 命令：`wsl -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && PYTHONPATH=. .venv/bin/pytest test/test_worldline_live_services.py::test_live_graph_timeline_and_stale_detector -q -vv'`
- 结果：124 秒超时，无有效 pytest 输出。
- 处理：超时后检查到残留 pytest 进程 `59506`，已执行 `wsl -d Debian -- kill 59506` 清理。
- 诊断：`-s` 重跑后确认卡在 collection/import 阶段；导入 `src.knowledge.compiler.models` 会触发 `src/__init__.py` 与 `src/knowledge/__init__.py` 的运行时 bootstrap，进而加载知识库和图数据库相关依赖。

## 2026-06-08 P0 增量修复

- 修改 `src/knowledge/__init__.py`：
  - 支持 `WORLDLINE_SKIP_APP_INIT=1`。
  - skip 模式下不注册 KB implementation、不创建 `KnowledgeBaseManager`、不创建 `UploadGraphService`。
  - 非 skip 模式保持原有运行时行为，用于 FastAPI 服务正常启动。
- 修改 `test/conftest.py`：
  - pytest 进程默认 `os.environ.setdefault("WORLDLINE_SKIP_APP_INIT", "1")`。
  - live API router tests 仍通过 HTTP 访问已经运行的 FastAPI 服务，不受本地测试进程 skip 影响。
- 修改 `test/test_kb_minio_cleanup.py`：
  - 当 skip 模式下 `knowledge_base is None` 时显式 skip，避免旧 MinIO 集成测试在 unit collection 中误触发运行时初始化。

## 2026-06-08 P0 API 闭环验证

### 临时种子数据

- 临时 DB：`codex_graph_20260608153125`。
- 种子方式：在 `api-dev` 容器内使用 `WORLDLINE_SKIP_APP_INIT=1` 直接写入 Postgres：
  - `KnowledgeBase(kb_type="codex_test")`
  - `KnowledgeFile`
  - `CompiledDocument`
  - `EvidenceAnchor`
  - `KnowledgeChunk`
- 选择 `codex_test` 类型是为了验证 graph/timeline router、service、repository 数据链路，同时避免为 QA 初始化 Milvus/LightRAG 外部运行时。

### 真实 HTTP endpoint 结果

- 临时管理员：`codex_temp_admin`，随机/一次性密码只在进程变量内使用，未写入仓库或总结。
- 登录 `/api/auth/token`：200。
- `POST /api/knowledge/databases/codex_graph_20260608153125/graph/rebuild`：200，`status=success`，`entities=12`，`relationships=28`，`temporal_facts=1`。
- `GET /api/knowledge/databases/codex_graph_20260608153125/graph/entities`：200，`items=12`。
- `GET /api/knowledge/databases/codex_graph_20260608153125/graph/relationships`：200，`items=28`。
- `GET /api/knowledge/databases/codex_graph_20260608153125/graph/conflicts`：200，`status=clean`，`conflict_count=0`。
- `GET /api/knowledge/databases/codex_graph_20260608153125/graph/neo4j-projection`：200，`status=ready`，`nodes=12`，`relationships=28`，`temporal_facts=1`。
- `GET /api/knowledge/databases/codex_graph_20260608153125/timeline`：200，`items=1`。

### 清理

- 临时 KB：已删除，`deleted_kb=1`。
- 临时管理员：已标记 `is_deleted=1`。
- 临时 Chrome profile：已删除。

## 2026-06-08 P0 截图 QA

- 桌面截图：`.ai/tasks/2026-06-08-graph-backend-data-chain/screenshots/graph-1440x900-authenticated.png`
  - 视口：1440x900。
  - URL：`http://127.0.0.1:5173/graph`。
  - 页面状态：登录态，显示“已连接”和“当前没有可用图谱，请先创建或接入知识库”。
  - 横向溢出：false。
  - 页面错误提示：无。
- 移动截图：`.ai/tasks/2026-06-08-graph-backend-data-chain/screenshots/graph-390x844-authenticated.png`
  - 视口：390x844。
  - URL：`http://127.0.0.1:5173/graph`。
  - 页面状态：登录态，核心控件和空图谱状态可读。
  - 横向溢出：false。
  - 页面错误提示：无。
- in-app browser 的 `Page.captureScreenshot` 在 `/graph` 上超时；最终使用本机 Chrome headless + DevTools Protocol 截图，并删除临时 profile。

## 2026-06-08 P0 后续验证

### `pytest test/test_worldline_live_services.py -q -vv`

- 命令：`wsl -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && timeout 240s env PYTHONPATH=. .venv/bin/pytest test/test_worldline_live_services.py -q -vv'`
- 结果：通过。
- 摘要：`4 passed, 1 warning in 13.21s`。

### `pytest test/test_knowledge_object_models.py test/test_evidence_service.py test/test_graph_router_adapter.py -q -vv`

- 命令：`wsl -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && timeout 180s env PYTHONPATH=. .venv/bin/pytest test/test_knowledge_object_models.py test/test_evidence_service.py test/test_graph_router_adapter.py -q -vv'`
- 结果：通过。
- 摘要：`16 passed, 1 warning in 16.58s`。

### `git diff --check`

- 命令：`git diff --check -- src/knowledge/__init__.py test/conftest.py test/test_kb_minio_cleanup.py server/routers/graph_router.py test/test_graph_router_adapter.py .ai/tasks/2026-06-08-graph-backend-data-chain`
- 结果：通过。
- 备注：仅有 `server/routers/graph_router.py`、`test/conftest.py`、`test/test_kb_minio_cleanup.py` 的 CRLF/LF 提示。

### `docker compose config --quiet`

- 命令：`wsl -d Debian --cd /mnt/d/dev/Worldline -- docker compose config --quiet`
- 结果：通过。

### `npm run docs:build`

- 命令：`wsl -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && npm run docs:build'`
- 结果：通过。
- 摘要：VitePress `build complete in 31.56s`。

### `npm --prefix web run build`

- 命令：`wsl -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && /home/joy/.local/bin/npm --prefix web run build'`
- 结果：通过。
- 摘要：Vite `built in 5m 39s`。
- 备注：仍有大 chunk warning，属于既有前端体积提示，不是本次 P0 行为失败。

### 残留进程检查

- `wsl -d Debian -- pgrep -af pytest`：无输出。

## 当前结论

- `/api/graph/*` 默认 Neo4j 路由不再表现为未登录外的 500；在当前空数据环境下返回 200 与空图谱。
- LightRAG graph adapter 不再被 Upload/Neo4j `graph_base` 启动硬阻塞。
- Worldline DB 级 graph/timeline 端点已通过临时 evidence-bound KB 做真实 HTTP 闭环验证。
- `/graph` 登录态桌面与 390px 移动端截图 QA 已完成，当前空图谱状态可解释且无横向溢出。
- P0 graph/timeline 后端链路与 `/graph` 基础 QA 已完成；后续转入 P1/P2：主题模块闭环、Agent Run Ledger、Dashboard 真实截图、全站 UI QA、上传/解析参数链路和工作树分组。
