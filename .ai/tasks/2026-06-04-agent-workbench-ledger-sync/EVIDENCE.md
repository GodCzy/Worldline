# Agent Workbench Ledger Sync Evidence

更新时间：2026-06-04

## 验证记录

### git diff --check

命令：

```powershell
git diff --check
```

结果：通过。仅输出既有工作树文件的 CRLF 提示。

### 前端构建

Windows 侧 `npm --prefix web run build` 不可用，原因是 Windows PowerShell 没有 `npm` 命令。改用 WSL Debian：

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
- 账本状态块存在。
- 保存到后端账本按钮存在。
- 技能候选提交按钮数量：2。
- 页面中存在 SVG/Canvas 节点：12。

截图：

- `D:\dev\Worldline\.ai\tasks\2026-06-04-agent-workbench-ledger-sync\screenshots\agent-ledger-sync-viewport.png`

限制：当前 in-app Browser 未暴露直接视口切换能力，项目本地也没有 Playwright 依赖，因此本阶段未额外生成移动端截图。

### 后端路由冒烟

OpenAPI 路由存在：

- `/api/worldline/runs`
- `/api/worldline/runs/{run_id}`
- `/api/worldline/runs/{run_id}/events`
- `/api/worldline/runs/{run_id}/branches/{branch_id}/approve`
- `/api/worldline/runs/{run_id}/branches/{branch_id}/reject`
- `/api/worldline/runs/{run_id}/skills/propose`

未登录写入保护：

```powershell
POST http://127.0.0.1:5050/api/worldline/runs
```

结果：`401`。

健康检查：

```powershell
GET http://127.0.0.1:5050/api/system/health
```

结果：`{"status":"ok","message":"服务正常运行"}`。

### Docker Compose 配置

Windows 侧没有 `docker` 命令，改用 WSL Debian：

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && docker compose config >/dev/null && echo 'docker compose config passed'"
```

结果：通过。
