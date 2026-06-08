# Agent Artifact Rail Evidence

更新时间：2026-06-04

## 代码验证

- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue web/src/data/worldline/agentWorkbench.js .ai/tasks/2026-06-04-agent-artifact-rail"`：通过。
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline/web && npm run build"`：通过，Vite 构建完成；仍有既有 large chunk warning。

## 浏览器验证

- 页面：`http://127.0.0.1:5173/worldline/agent`。
- Artifact Rail 已显示在 Evidence Rail 与 Tool Trace 之间。
- 初始 Branch 视角：`Branch 2`，展示 `Workflow plan` 与 `Quality gate report`。
- Event 视角：`Event 4`，展示 `Evidence dossier`、`Workflow plan`、`Quality gate report`、`Skill genome draft`。
- All 视角：`All 4`。
- 点击 `Skill genome draft` 后：
  - `Focus Dossier` 标题为 `Skill genome draft`。
  - badge 为 `json`。
  - meta 包含 `Artifact ID=artifact-skill-genome`、`Path=.ai/tasks/agent-workbench/skill-genome.json`、`Tool Call=tool-propose-skill`、`Branch=技能进化分支`。
  - Artifact Rail 条目和事件详情 token 均进入 focused 状态。
- 当前 1280px 视口检查 `documentElement.scrollWidth`，无横向溢出。

## 截图

- `D:\dev\Worldline\.ai\tasks\2026-06-04-agent-artifact-rail\screenshots\artifact-rail-event-dossier.png`
- `D:\dev\Worldline\.ai\tasks\2026-06-04-agent-artifact-rail\screenshots\artifact-rail-focus-dossier.png`

## 受限项

- 本阶段未改后端代码，因此未重复运行后端 pytest。
- Browser 插件上一阶段已确认不支持 `tab.playwright.setViewportSize`，本阶段未做 390px 真实移动视口截图。
