# Phase 86 - Phase 6 Round 1 Runtime Smoke Green

## Summary
- Phase 6 第一轮的 `worldline-ops` 最小接入骨架已完成真实后端在线条件下的 runtime smoke。
- 当前 `api/system/info` 已可访问，`/themes`、`/themes/worldline-ops`、`/worldline`、`/worldline/worldline-ops` 已经通过真实 `5173 -> 5050` 链路完成验证。
- 本轮为了恢复后端可用性，只做了一个最小后端补丁：将应用启动从 Neo4j 导入时硬依赖中解开，使公开信息接口可以在图谱服务离线时独立启动。
- 当前唯一已清零的主阻塞项是：`本机真实后端 api/system/info 不在线`。

## Actual Subagent Decomposition
本轮实际并行运行并回收了以下子代理：
- `system_mapper`
  - 结论：Phase 6 第一轮第二模块骨架仍严格停留在允许边界内。
  - 真实接入文件仍只有：
    - `src/config/static/info.template.yaml`
    - `web/src/data/worldline/index.js`
    - `web/src/data/worldline/worldlineOpsAdapter.js`
- `product_architect`
  - 结论：`worldline-ops` 仍是正确试点对象，当前骨架已经满足最小门槛，允许本轮不扩功能。
- `frontend_worker`
  - 结论：`/themes`、`/themes/worldline-ops`、`/worldline`、`/worldline/worldline-ops` 的前端发现链已经完整，页面层无需补丁。
- `backend_worker`
  - 初始判断偏向“环境未启动”。
  - 控制器随后用真实启动日志纠正该判断：实际阻塞是应用导入阶段对 Neo4j 的硬依赖，而不仅仅是 Docker 未启动。
- `qa_release_auditor`
  - 结论：如果真实后端在线并完成浏览器级 smoke，则 Phase 6 第一轮即可视为稳定基线。

## Actual Changes
- [src/__init__.py](../../src/__init__.py)
  - 增加默认的 `graph_base = None` 和 `knowledge_base = None`。
  - 修正 `YUXI_SKIP_APP_INIT=1` 时 `from src import graph_base` 会直接 ImportError 的问题。
- [src/knowledge/__init__.py](../../src/knowledge/__init__.py)
  - 将 `UploadGraphService()` 的导入期初始化改为容错启动。
  - 当 Neo4j 不可达时，不再让整个应用在 import 阶段崩溃，而是记录 warning 并延后到运行时恢复。

## Why This Was Needed
- 真实启动日志显示，`uvicorn server.main:app` 在导入 `server.main -> server.routers -> src -> src.knowledge` 的过程中，会立即实例化 `UploadGraphService()`。
- 当 Neo4j 不在线时，这一步会直接抛出连接异常，导致：
  - `api/system/info` 无法启动
  - 前端真实主题发现链路无法使用真实后端完成 smoke
- 这个问题不属于第二模块功能缺口，而属于平台启动链耦合过重。
- 最小合理补丁不是去扩第二模块，也不是去补 Docker 文档，而是让公开信息接口从图谱连接初始化里解耦。

## Runtime Smoke Evidence
### API level
- `Invoke-RestMethod http://127.0.0.1:5050/api/system/info`
  - 返回 `success = true`
  - 返回主题列表包含：
    - `poe`
    - `worldline-ops`

### Browser level
- 真实浏览器通过 Playwright MCP 访问本机开发链路：
  - `http://127.0.0.1:5173/themes`
  - `http://127.0.0.1:5173/themes/worldline-ops`
  - `http://127.0.0.1:5173/worldline`
  - `http://127.0.0.1:5173/worldline/worldline-ops`
  - `http://127.0.0.1:5173/themes/poe`
  - `http://127.0.0.1:5173/worldline/poe`
- 已确认：
  - `/themes` 页面同时显示 `流放之路` 与 `运营验证`
  - `/themes/worldline-ops` 页面可进入，标题为 `运营验证`
  - `/worldline` 页面可见两个模块 pill
  - `/worldline/worldline-ops` 可进入并生成最小世界线
  - `/themes/poe` 与 `/worldline/poe` 未回退
  - 浏览器真实请求记录中存在：
    - `GET /api/system/info => 200`

### Source-level guards
- 页面层与共享层未重新吃模块私有结构：
  - `web/src/views/**`
  - `web/src/components/**`
  - `web/src/stores/**`
  - 未新增对 `@/data/poePhase1` 的直接依赖
  - 未新增对具体 adapter 文件的页面级直连

## Validation
已完成：
- `python -m py_compile D:\worldline\src\__init__.py D:\worldline\src\knowledge\__init__.py`
- `Invoke-RestMethod http://127.0.0.1:5050/api/system/info`
- Playwright MCP 真实浏览器 smoke

本轮未新增但继承仍有效：
- `pnpm --dir D:\worldline\web build`
- `npm --prefix D:\worldline run docs:build`

## Result
- Phase 6 第一轮已完成并可作为稳定基线。
- 当前已经不再只剩“后端可用性问题”，因为这个问题已被本轮最小补丁清除。
- 当前阶段剩余问题不再属于 Phase 6 第一轮收尾，而属于下一轮要不要继续扩第二模块能力面的阶段决策。

## Remaining Risks
- 图谱服务本身仍未恢复，`graph_base` 当前可能为空。
- 这不会阻断 `api/system/info` 和第二模块发现链，但图谱专用能力仍然依赖后续 Neo4j 运行时恢复。
- 本轮没有把 `server/**` 大规模解耦，只修了启动链上的最小硬阻塞点。

## Phase Judgment
- current phase: `Phase 6 / round 1 complete`
- readiness for next phase: `ready for Phase 6 round 2 planning`
- main remaining gap: `决定第二模块下一轮是继续丰富运营能力，还是先引入第三模块来验证多模块契约`
