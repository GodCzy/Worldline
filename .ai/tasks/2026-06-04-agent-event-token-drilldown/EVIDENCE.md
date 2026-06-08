# Agent Event Token Drilldown Evidence

更新时间：2026-06-04

## 验证记录

### 差异检查

- 命令：`git diff --check`
- 结果：通过。
- 备注：仅有既有 CRLF/LF 换行提示。

### 前端构建

- 命令：`wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- 结果：通过。
- 耗时：约 4m21s。
- 备注：Vite 仍提示已有大 chunk warning，本阶段未新增构建错误。

### 浏览器验证

- URL：`http://127.0.0.1:5173/worldline/agent`
- 初始状态：
  - `.event-detail-token` 共 7 个。
  - disabled token 为 0。
  - Evidence Rail 和 Timeline Scrubber 均存在。
- 点击检查：
  - `tool-plan-workflow` -> 高亮 `worldline.plan_workflow`。
  - `ev-agent-workflow` -> Evidence Rail 切到 `Evidence 3`，并高亮 `evidence:ev-agent-workflow`。
  - `tf-stage1` -> Evidence Rail 切到 `Time 2`，并同时高亮 `timeline:tf-stage1` rail item 和 Timeline Scrubber temporal item。
  - `worldline_service_boundary` -> 高亮 `worldline.plan_workflow` 与 `worldline.run_quality_gate` 两个同权限工具调用。
  - `run-agent-workbench-preview` -> 切到技能进化分支，并高亮 `Agent Ledger Review`。
- 截图：`D:\dev\Worldline\.ai\tasks\2026-06-04-agent-event-token-drilldown\screenshots\agent-event-token-drilldown.png`

### 后端冒烟

- OpenAPI：确认以下路径仍暴露：
  - `/api/worldline/runs`
  - `/api/worldline/runs/{run_id}`
  - `/api/worldline/runs/{run_id}/events`
  - `/api/worldline/runs/{run_id}/branches/{branch_id}/approve`
  - `/api/worldline/runs/{run_id}/branches/{branch_id}/reject`
  - `/api/worldline/runs/{run_id}/skills/propose`
- Health：`GET /api/system/health` 返回 `status: ok`。
- Compose：`docker compose config passed`。
