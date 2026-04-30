# Phase 76 - Phase 5 Live API Regression Green And Coupling Classification

## Summary

- Phase 5 第三轮完成了两件事：
  - 复核前端剩余 `poePhase1` 耦合边界，确认页面层已清零，剩余直连仅保留在模块 adapter 边界。
  - 实际跑通 live API 集成回归，并把阻塞从“凭据缺失”推进到“环境代理 + 后端兼容细节”，最终收口为全绿。
- 本轮没有扩业务功能，没有改变 Phase 4 已冻结的 graph/auth 权限语义。

## Subagent Decomposition

1. `system_mapper`
   - 扫描 `web/src/views` 与 `web/src` 中对 `@/data/poePhase1` 的直接依赖。
   - 结论：页面层直接依赖已清零，仅 `web/src/data/worldline/poeWorldlineAdapter.js` 保留模块层直连。
2. `product_architect`
   - 复核 Phase 5 边界。
   - 结论：`poeWorldlineAdapter.js` 作为模块 adapter 边界允许保留；共享页面不得再次直接 import 模块数据源。
3. `frontend_worker`
   - 只读复核共享层是否仍有必须继续解耦的页面。
   - 结论：当前没有新的“必须立刻改”的共享层文件；后续若继续去 PoE 语义，应从页面内容层而不是数据 import 层推进。
4. `backend_worker`
   - 参与 live API 回归问题定位。
   - 主控最终依据真实回归证据，在最小范围内完成后端兼容补丁。
5. `qa_release_auditor`
   - 明确最小回归命令、通过标准与 blocker。
   - 本轮主控实际按该路径完成 live API 回归执行。

## Stable Conclusions

### Remaining `@/data/poePhase1` Direct Imports

1. `web/src/data/worldline/poeWorldlineAdapter.js`

边界判断：
- 允许保留在模块层：`web/src/data/worldline/poeWorldlineAdapter.js`
- 页面层必须继续保持 0 个 direct import：`web/src/views/**`

### Live API Regression Outcome

已实际跑通：

```powershell
$env:TEST_BASE_URL="http://127.0.0.1:5050"
$env:TEST_USERNAME="worldline_admin"
$env:TEST_PASSWORD="Worldline123!"
uv run --group test pytest -q test/api/test_graph_router_list.py test/api/test_unified_graph_router.py -m integration
```

结果：
- `12 passed in 5.27s`
- 匿名 `/api/graph/*` 权限边界通过
- 普通用户 `/api/graph/*` 权限边界通过
- 管理员 graph list / stats / deprecated compatibility routes 全部通过

### Root Causes Closed In This Round

1. `test/conftest.py`
   - live API 集成测试原先会继承系统代理环境，导致对本地 `127.0.0.1:5050` 的请求异常走代理并返回 `502`。
   - 处理：统一为 `httpx.AsyncClient(..., trust_env=False)`，强制本地直连。
2. `server/routers/graph_router.py`
   - `knowledge_base.is_lightrag_database(db_id)` 漏掉 `await`，导致 `neo4j` stats 错误走 LightRAG 分支。
   - 处理：补上 `await`，恢复 `neo4j` 统计信息返回。
3. `src/knowledge/graphs/upload_graph_service.py`
   - 旧兼容查询在无向量索引时直接抛异常，导致 `/api/graph/neo4j/node` 对空图谱场景返回 `500`。
   - 处理：降级为 fuzzy-only 查询；无索引时返回空结果而不是抛错。
4. `test/api/test_unified_graph_router.py`
   - 默认图谱当前通过 upload adapter facade 暴露，测试中写死 `type == "neo4j"` 已与现行契约不符。
   - 处理：更新为 `type == "upload"`，并检查 `capabilities` 字段存在。

## Files Changed In This Round

1. `test/conftest.py`
   - 新增统一 `HTTP_CLIENT_KWARGS`
   - 所有 live API `httpx.AsyncClient` 统一加 `trust_env=False`
2. `server/routers/graph_router.py`
   - 修复 `get_graph_stats` 中 `is_lightrag_database` 漏 `await`
3. `src/knowledge/graphs/upload_graph_service.py`
   - 无向量索引时改为 warning + 空结果降级，不再抛异常打断兼容路由
4. `test/api/test_unified_graph_router.py`
   - 更新默认图谱类型断言以匹配当前稳定契约

## Validation

已通过：

```powershell
Get-ChildItem -Path D:\worldline\web\src\views -Recurse -File | Select-String -Pattern '@/data/poePhase1'
Get-ChildItem -Path D:\worldline\web\src -Recurse -File | Select-String -Pattern '@/data/poePhase1'
python -m py_compile D:\worldline\test\conftest.py D:\worldline\server\routers\graph_router.py D:\worldline\src\knowledge\graphs\upload_graph_service.py
$env:TEST_BASE_URL='http://127.0.0.1:5050'; $env:TEST_USERNAME='worldline_admin'; $env:TEST_PASSWORD='Worldline123!'; uv run --group test pytest -q test/api/test_graph_router_list.py test/api/test_unified_graph_router.py -m integration
```

验证结论：
- `web/src/views/**` 中已无 direct import `@/data/poePhase1`
- 当前仓库唯一 direct import 位于允许保留的模块 adapter：`web/src/data/worldline/poeWorldlineAdapter.js`
- live API graph 回归已全绿

## Phase Judgment

- current phase: `Phase 5 / coupling cleanup and compatibility hardening`
- readiness for next phase: `not ready yet`
- main remaining gap:
  - 继续判断共享页面中的 PoE 专有展示语义是否需要进一步抽离
  - 继续做文档与仓库冗余收口，而不是停留在当前“结构可用但仍偏厚”的状态
