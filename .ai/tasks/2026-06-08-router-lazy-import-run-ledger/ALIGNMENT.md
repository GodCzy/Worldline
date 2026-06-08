# Alignment

日期：2026-06-08

## 目标

修复 `test/test_worldline_run_ledger_service.py` 在 collection 阶段超时的问题，让 Run Ledger 后端契约测试可以作为当前证据运行。

## 验收

- 导入 `server.routers.worldline_run_router` 不再触发所有 router 的顶层导入。
- `test/test_worldline_run_ledger_service.py --collect-only` 能在合理时间内完成。
- Run Ledger 相关测试文件能运行并通过。
- 生产入口 `from server.routers import router` 仍然可用并能构建完整 API router。

## 边界

- 不改任何具体业务 router 的请求/响应契约。
- 不新增数据库 schema。
- 不回滚未知工作树改动。
