# Tasks

日期：2026-06-08

- [x] 读取 `2026-06-08-Worldline-Next-Goal-Unfinished-Work.md`、项目规则与当前事实源。
- [x] 确认未登录访问 `/api/graph/list` 返回 401，受保护 API 需要管理员登录。
- [x] 使用本地临时 `codex_temp_admin` superadmin 完成真实 API 探测，并在 QA 后清理账号。
- [x] 诊断 `/api/graph/*` 与 `/api/knowledge/databases/{db_id}/graph/*` 的接口边界。
- [x] 修复 `server/routers/graph_router.py` 中 `_get_graph_adapter()` 的类型边界。
- [x] 补充 `test/test_graph_router_adapter.py` focused tests。
- [x] 运行 focused unit test 与 live API integration test。
- [x] 运行 `git diff --check`、`docker compose config --quiet`、`npm run docs:build`。
- [x] 记录 `test_worldline_live_services` 当前超时限制。
- [x] 写入 OutputMD 阶段总结和完整未完成事项交接。
- [x] 修复 pytest collection/import 阶段触发知识库和图数据库 bootstrap 的问题。
- [x] 重跑并通过 `test/test_worldline_live_services.py` 全文件。
- [x] 用临时 evidence-bound KB 验证 DB 级 graph/timeline HTTP endpoints。
- [x] 完成 `/graph` 登录态桌面和 390px 移动端截图 QA。
- [x] 清理临时 KB、临时管理员和临时 Chrome profile。

## 仍未完成

- [ ] 将 graph 链路与后续 P1/P2 工作纳入分组提交或下一轮目标模式。
- [ ] 继续处理主题模块闭环、Agent Run Ledger、Dashboard 真实截图、全站 UI QA、上传/解析参数链路和工作树分组。
