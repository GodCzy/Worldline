# 证据

## 已确认

- `DashboardView.vue` 原本已有部分 Worldline 深色变量，但统计卡片、Ant Design 表格、输入框、选择器、分页和下拉层仍会露出浅色默认样式。
- `cleanupCharts()` 中 `toolStatsRef` 分支误调用了 `userStatsRef.cleanup()`。

## 本次修改

- 为 Dashboard 根节点加入 `layout-container wl-ant-dark`，让页面进入统一的 Worldline 深色上下文。
- 增加页面级 Ant Design 深色覆盖，覆盖 statistic、divider、table、input、select、button、pagination、loading、empty 和 dropdown/menu。
- 修正 `cleanupCharts()` 中 `toolStatsRef` 的 cleanup 调用。

## 验证

- `git diff --check -- web/src/views/DashboardView.vue .ai/tasks/2026-06-07-dashboard-dark-unification`：通过；仅出现 Git 对 CRLF/LF 转换的提示，不是 diff 格式错误。
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && /home/joy/.local/bin/npm --prefix web run build"`：通过；保留 Vite 现有的大 chunk 警告。
- in-app Browser 打开 `http://127.0.0.1:5173/dashboard`：当前浏览器未登录管理员，路由守卫重定向到 `/?login=1&redirect=/dashboard`；说明未认证状态不会直接暴露运营看板。由于没有管理员会话，本阶段未强行绕过权限截图。

## 残余限制

- `/dashboard` 的真实视觉截图仍需要 Joy 使用管理员账号登录后再验收。
- 本阶段没有修改统计 API、图表数据结构或后端契约。
