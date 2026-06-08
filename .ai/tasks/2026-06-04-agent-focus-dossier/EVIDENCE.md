# Agent Focus Dossier Evidence

更新时间：2026-06-04

## 验证记录

### 差异检查

- 命令：`git diff --check`
- 结果：通过。
- 备注：仅有既有 CRLF/LF 换行提示。

### 前端构建

- 命令：`wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- 结果：通过。
- 耗时：约 4m07s。
- 备注：Vite 仍提示已有大 chunk warning，本阶段未新增构建错误。

### 浏览器验证

- URL：`http://127.0.0.1:5173/worldline/agent`
- 初始状态：
  - `.event-detail-token` 共 7 个。
  - 未点击 token 前不存在 `[data-inspector-dossier="true"]`，避免占用初始事件详情空间。
- Dossier 点击检查：
  - `ev-agent-workflow` -> Evidence Dossier：标题 `Controlled Agent workflow lanes`，包含 `Source`、`Location`、`Graph Links`。
  - `tool-plan-workflow` -> Tool Dossier：标题 `worldline.plan_workflow`，包含 `Permission`、`Branch`、`Result`。
  - `tf-stage1` -> Timeline Dossier：标题 `Stage 1 local ledger preview`，包含 `Valid From`、`Valid To`、`Evidence`。
  - `worldline_service_boundary` -> Permission Dossier：列出 `worldline.plan_workflow` 与 `worldline.run_quality_gate` 两个同权限工具调用。
  - `run-agent-workbench-preview` -> Skill Dossier：标题 `Agent Ledger Review`，包含 `Skill ID`、`Status`、`Permissions`、`Evidence Runs` 和步骤列表。
- 截图：`D:\dev\Worldline\.ai\tasks\2026-06-04-agent-focus-dossier\screenshots\agent-focus-dossier.png`

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
