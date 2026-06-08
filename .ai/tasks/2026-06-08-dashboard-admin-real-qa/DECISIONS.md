# Decisions

- 为 Dashboard QA 使用独立临时管理员 `codex_dash_admin`。原因：和 Agent Workbench E2E 的临时账号隔离，便于证据和清理追踪。
- 先跑 API shape check 再截图。原因：如果页面空状态异常，可以区分是接口问题还是前端呈现问题。
- 截图保留 `.jpg` 扩展名。原因：Browser screenshot 当前返回 JPEG 字节。
