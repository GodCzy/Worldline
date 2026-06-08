# Alignment

目标：补齐 `/dashboard` 管理员真实登录态 QA，验证统计 API、空状态和深色界面，而不是停留在未登录跳转。

范围：
- 使用当前本地后端 `http://127.0.0.1:5050` 和 Vite `http://127.0.0.1:5173`。
- 准备本地临时管理员 `codex_dash_admin`，完成后清理。
- 验证 Dashboard 统计 API、conversations、feedbacks 和 timeseries 返回结构。
- 浏览器中真实登录后打开 `/dashboard`。
- 完成桌面和 `390x844` 移动端截图 QA。

不做：
- 不伪造管理员截图。
- 不绕过路由守卫。
- 不整理无关脏工作树。
