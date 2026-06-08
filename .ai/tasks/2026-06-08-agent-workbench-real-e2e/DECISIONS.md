# Decisions

- 使用真实后端 `/api/worldline/runs` 作为 E2E 判断依据。原因：本阶段要证明 Agent Workbench 不只是本地 preview。
- 不把临时管理员密码写入文件。原因：避免凭据落盘。
- 浏览器 QA 先用真实 API 准备 run，再在页面中刷新、选择并载入 Manifest。原因：页面登录态脚本环境不暴露 `fetch/localStorage`，走 UI 控件更接近真实用户路径。
- E2E run 完成截图后只归档不删除。原因：当前 run ledger API 提供 archive/restore 维护语义，没有删除接口；归档保留审计轨迹且不污染默认 approved 列表。
