# Agent Gate Run Panel Evidence

更新时间：2026-06-04

## 代码验证

- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue web/src/data/worldline/agentWorkbench.js .ai/tasks/2026-06-04-agent-gate-run-panel"`：通过。
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline/web && npm run build"`：通过，Vite 构建完成；仍有既有 large chunk warning。

## 浏览器验证

- 页面：`http://127.0.0.1:5173/worldline/agent`。
- Quality Gates 面板已升级为 Gate Run Panel。
- 初始 Branch 视角：`Branch 2`，展示 `Permission risk` 与 `Temporal conflict`。
- Event 视角：`Event 4`，展示 4 个 gate。
- All 视角：`All 4`。
- Gate Run 条目展示 `Value`、`Threshold`、`Input`、`Artifacts` 和 remediation 文案。
- 点击 `Permission risk` 后：
  - `Focus Dossier` 标题为 `Permission risk`。
  - badge 为 `review`。
  - meta 包含 `Gate ID=gate-permission`、`Status=review`、`Value=2 approvals`、`Threshold=0 unapproved write-like actions`、`Input=2 worldline_service_boundary tool calls pending approval`、`Failure=Workflow execution is planned but still requires human approval.`、`Remediation=Approve the branch, reject the action, or split the write step into a narrower branch.`。
  - Gate Run 条目和事件详情 token 均进入 focused 状态。
- 当前 1280px 视口检查 `documentElement.scrollWidth`，无横向溢出。

## 截图

- `D:\dev\Worldline\.ai\tasks\2026-06-04-agent-gate-run-panel\screenshots\gate-run-focus-dossier.png`
- `D:\dev\Worldline\.ai\tasks\2026-06-04-agent-gate-run-panel\screenshots\gate-run-dossier-meta.png`

## 受限项

- 本阶段未改后端代码，因此未重复运行后端 pytest。
- Browser 插件当前不支持 `tab.playwright.setViewportSize`，未做 390px 真实移动视口截图。
