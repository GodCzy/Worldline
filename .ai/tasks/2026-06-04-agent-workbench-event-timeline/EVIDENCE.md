# Agent Workbench Event Timeline Evidence

更新时间：2026-06-04

## 验证记录

### git diff --check

命令：

```powershell
git diff --check
```

结果：通过。仅输出既有工作树文件的 CRLF 提示。

### 前端构建

命令：

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"
```

结果：通过。Vite 构建成功，仍有既有的大 chunk warning。

### 浏览器验证

目标：

```text
http://127.0.0.1:5173/worldline/agent
```

DOM 检查结果：

- 页面标题包含 `Agent 工作台`。
- `RUN EVENTS` 面板存在。
- `All / Run / Branch / Tool / Skill` 过滤按钮都存在。
- 事件卡片数量：4。
- 预览事件数量：4。
- 页面中存在 SVG/Canvas 节点：12。

截图：

- `D:\dev\Worldline\.ai\tasks\2026-06-04-agent-workbench-event-timeline\screenshots\agent-event-timeline-viewport.png`
- `D:\dev\Worldline\.ai\tasks\2026-06-04-agent-workbench-event-timeline\screenshots\agent-event-panel-header-viewport.png`

### 后端路由冒烟

OpenAPI 路由存在：

- `/api/worldline/runs`
- `/api/worldline/runs/{run_id}`
- `/api/worldline/runs/{run_id}/events`
- `/api/worldline/runs/{run_id}/branches/{branch_id}/approve`
- `/api/worldline/runs/{run_id}/branches/{branch_id}/reject`
- `/api/worldline/runs/{run_id}/skills/propose`

未登录读取 events：

```powershell
GET http://127.0.0.1:5050/api/worldline/runs/smoke/events
```

结果：`401`，说明事件流仍受 admin 保护。

健康检查：

```powershell
GET http://127.0.0.1:5050/api/system/health
```

结果：`{"status":"ok","message":"服务正常运行"}`。

### Docker Compose 配置

命令：

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && docker compose config >/dev/null && echo 'docker compose config passed'"
```

结果：通过。
