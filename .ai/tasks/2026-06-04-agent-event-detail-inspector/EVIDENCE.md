# Agent Event Detail Inspector Evidence

更新时间：2026-06-04

## 验证记录

### 前端构建

- 命令：`wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- 结果：通过。
- 备注：Vite 仍提示已有 chunk size warning，本阶段未引入新的构建错误。

### 浏览器验证

- URL：`http://127.0.0.1:5173/worldline/agent`
- 检查项：
  - `.agent-workbench` 渲染存在。
  - `.event-item` 共 4 条。
  - `.event-item.selected` 始终为 1 条。
  - `.event-detail` 渲染存在。
  - 默认事件详情展示 Evidence / Tool / Timeline token。
  - 点击 `.event-item.kind-tool` 后详情切换为 `Tool Pending`，并展示 `tool-plan-workflow`、`tool-run-quality-gate` 和 `worldline_service_boundary`。
- 截图：`D:\dev\Worldline\.ai\tasks\2026-06-04-agent-event-detail-inspector\screenshots\agent-event-detail-inspector.png`

### 后端路由冒烟

- OpenAPI：`http://127.0.0.1:5050/openapi.json`
- 已暴露路径：
  - `/api/worldline/runs`
  - `/api/worldline/runs/{run_id}`
  - `/api/worldline/runs/{run_id}/events`
  - `/api/worldline/runs/{run_id}/branches/{branch_id}/approve`
  - `/api/worldline/runs/{run_id}/branches/{branch_id}/reject`
  - `/api/worldline/runs/{run_id}/skills/propose`
- Health：`GET /api/system/health` 返回 `status: ok`。
- Auth：未认证访问 `GET /api/worldline/runs/smoke/events` 返回 `401`，符合当前鉴权边界。

### 配置与差异检查

- 命令：`git diff --check`
- 结果：通过。
- 备注：仅有既有 CRLF/LF 换行提示。
- 命令：`wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && docker compose config >/dev/null && echo 'docker compose config passed'"`
- 结果：`docker compose config passed`
