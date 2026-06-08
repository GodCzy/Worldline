# Design

## 问题

Python 导入 `server.routers.worldline_run_router` 前会先执行包级 `server/routers/__init__.py`。旧实现会在包级顶层导入所有 router 并立即构建 `router = create_api_router()`，导致只想测试 Run Ledger 的文件也会牵连 chat、knowledge、system、graph 等重模块。

## 方案

- 将 `server/routers/__init__.py` 改为 router spec 表。
- `create_api_router()` 执行时才用 `import_module()` 加载具体 router。
- 用 `__getattr__("router")` 兼容 `from server.routers import router`，并缓存完整 router。
- 单个子 router import 不再触发完整 API router 构建。

## 验证

- 直接导入 `server.routers.worldline_run_router`。
- 直接 `from server.routers import router` 并检查 route 数。
- `pytest --collect-only test/test_worldline_run_ledger_service.py`。
- 运行 Run Ledger 相关 focused pytest。
