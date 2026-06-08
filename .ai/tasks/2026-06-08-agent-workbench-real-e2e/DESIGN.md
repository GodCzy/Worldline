# Design

Agent Workbench E2E 采用真实 API 优先：

- 后端契约以 `server/routers/worldline_run_router.py` 为准。
- 前端 API 以 `web/src/apis/worldline_api.js` 的 `worldlineRunApi` 为准。
- 页面以 `web/src/views/worldline/WorldlineAgentWorkbenchView.vue` 为准。

验证策略：
- 若 dev server 可用，通过浏览器登录管理员并点击页面控件完成真实 E2E。
- 若页面控件难以稳定自动化，先用 authenticated HTTP 验证 API，再用页面截图验证可视状态和无明显控制台错误。
- 所有临时账号和临时 run 只用于本地 QA，密码不写入仓库或总结。
