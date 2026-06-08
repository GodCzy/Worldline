# Agent Event Evidence Links Evidence

更新时间：2026-06-04

## 验证记录

### Python 编译

命令：

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && python3 -m py_compile src/services/worldline_run_ledger_service.py server/routers/worldline_run_router.py test/test_worldline_run_ledger_service.py"
```

结果：通过。

### Focused Pytest

命令：

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && docker compose exec -T api python -m pytest test/test_worldline_run_ledger_service.py"
```

结果：`2 passed, 3 warnings`。

新增覆盖：

- `run.created` summary 包含 `evidenceIds`、`toolCallIds`、`temporalFactIds`。
- `branch.approved` summary 包含 `branch_title`、`evidenceIds`、`toolCallIds`、`temporalFactIds`。
- `skill.proposed` summary 包含 `requiredPermissions`、`evidenceRunIds`。

### git diff --check

命令：

```powershell
git diff --check
```

结果：通过。仅输出既有工作树文件 CRLF 提示。

### 前端构建

命令：

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"
```

结果：通过。Vite 构建成功，仍有既有大 chunk warning。

### 浏览器验证

目标：

```text
http://127.0.0.1:5173/worldline/agent
```

DOM 检查结果：

- `RUN EVENTS` 面板存在。
- 事件卡片数量：4。
- `event-link-chip` 数量：10。
- Evidence / Tool / Timeline / Permission chips 均存在。
- 事件卡片高度稳定，截图无明显文本重叠。

截图：

- `D:\dev\Worldline\.ai\tasks\2026-06-04-agent-event-evidence-links\screenshots\agent-event-evidence-chips.png`

### 后端冒烟

OpenAPI 路由存在：

- `/api/worldline/runs`
- `/api/worldline/runs/{run_id}`
- `/api/worldline/runs/{run_id}/events`
- `/api/worldline/runs/{run_id}/branches/{branch_id}/approve`
- `/api/worldline/runs/{run_id}/branches/{branch_id}/reject`
- `/api/worldline/runs/{run_id}/skills/propose`

健康检查：

```powershell
GET http://127.0.0.1:5050/api/system/health
```

结果：`{"status":"ok","message":"服务正常运行"}`。

未登录读取 events：

```powershell
GET http://127.0.0.1:5050/api/worldline/runs/smoke/events
```

结果：`401`。

### Docker Compose 配置

命令：

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && docker compose config >/dev/null && echo 'docker compose config passed'"
```

结果：通过。
