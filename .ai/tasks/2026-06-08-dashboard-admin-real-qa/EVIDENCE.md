# Evidence

日期：2026-06-08

## 临时管理员

- 创建/更新命令：在 `api` compose 服务中运行 `scripts/ensure_superadmin.py`。
- 账号：`codex_dash_admin`。
- 结果：`action=created`，`role=superadmin`，`password_verified=true`。
- 密码未写入文件或总结。

## Dashboard API Shape Check

- QA 脚本：`.ai/tasks/2026-06-08-dashboard-admin-real-qa/check_dashboard_real_api.py`。
- API base：`http://127.0.0.1:5050`。
- 覆盖接口：
  - `POST /api/auth/token`
  - `GET /api/dashboard/stats`
  - `GET /api/dashboard/stats/users`
  - `GET /api/dashboard/stats/tools`
  - `GET /api/dashboard/stats/knowledge`
  - `GET /api/dashboard/stats/agents`
  - `GET /api/dashboard/stats/calls/timeseries?type=models&time_range=14days`
  - `GET /api/dashboard/conversations?status=active&limit=8&offset=0`
  - `GET /api/dashboard/feedbacks?rating=all`
- 结果摘要：
  - `status=ok`
  - `admin_role=superadmin`
  - `total_users=2`
  - `total_calls=0`
  - `total_databases=0`
  - `agent_total=0`
  - `conversation_count=0`
  - `feedback_count=0`
- 结论：当前是空数据环境，但接口返回结构稳定，前端可消费。

## 浏览器 QA

- 登录路径：`/?login=1&redirect=/dashboard`。
- 成功页面：`http://127.0.0.1:5173/dashboard`。
- 页面状态：
  - 显示 `晚上好！codex_dash_admin`。
  - 顶部统计：`0 总对话数`、`0 活跃对话`、`0 总消息数`、`2 用户数`、`0 总反馈数`、`100% 满意度`。
  - Dashboard 文案与模块出现：`运营总览`、`调用统计`、`用户活跃度分析`、`AI智能体分析`、`工具调用监控`、`知识库使用情况`、`近期对话`。
  - 空数据表格显示 `暂无数据`，没有显示统计加载失败或对话列表加载失败。

## 移动端修复

- 首轮 `390x844` 截图发现：
  - StatusBar 的 `任务中心` 按钮被挤成竖排。
  - `调用统计` 筛选按钮在卡片头部竖排/截断。
- 修复文件：
  - `web/src/components/StatusBar.vue`
  - `web/src/components/dashboard/CallStatsComponent.vue`
- 修复内容：
  - 480px 以下 `任务中心` 仅显示图标按钮，用户名用 ellipsis。
  - 768px 以下 `CallStatsComponent` 卡片头部改成纵向布局，筛选按钮换行且保持 `white-space: nowrap`。

## 截图 QA

- 桌面截图：
  `D:\dev\Worldline\.ai\tasks\2026-06-08-dashboard-admin-real-qa\screenshots\dashboard-admin-real-desktop-1280x720.jpg`
- 390px 移动端截图：
  `D:\dev\Worldline\.ai\tasks\2026-06-08-dashboard-admin-real-qa\screenshots\dashboard-admin-real-mobile-390x844.jpg`
- 观察结果：
  - 桌面深色 UI 统一，统计卡片、图表区、空状态表格可读。
  - 移动端修复后，任务中心不再竖排，调用统计筛选不再截断。
  - 移动端用户名会按预期截断，避免挤压右侧图标按钮。

## 控制台与构建

- 控制台：
  - 未发现 error/warning 级别错误。
  - 有 ECharts 兼容提示：`Specified grid.containLabel but no use(LegacyGridContainLabel); use grid.outerBounds instead.` 该提示为现有 ECharts 配置提示，未阻塞渲染。
- `npm --prefix web run build`：通过，用时约 5 分钟；保留既有大 chunk warning。
- `python3 -m py_compile`：通过。
- `git diff --check`：通过；仅有既有 CRLF/LF warning。

## 清理

- 清理脚本：`.ai/tasks/2026-06-08-dashboard-admin-real-qa/cleanup_dashboard_admin.py`。
- `codex_dash_admin` 已标记 `is_deleted=1`。
- 再次登录验证：返回 403，符合预期。

## 残余说明

- Vite dev server 仍在运行，供后续 QA 复用。
- Dashboard 仍有 ECharts `grid.containLabel` 兼容提示，可后续统一 chart option 时处理。
