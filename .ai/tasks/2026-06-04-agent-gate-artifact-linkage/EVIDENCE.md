# Gate Artifact Linkage Evidence

## Static Checks

- `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue web/src/data/worldline/agentWorkbench.js .ai/tasks/2026-06-04-agent-gate-artifact-linkage`
  - Result: passed with no output.
  - Note: the active reset worktree still has these Worldline frontend files untracked, so an additional direct whitespace scan was run.
- `rg -n "[ \t]+$" web/src/views/worldline/WorldlineAgentWorkbenchView.vue web/src/data/worldline/agentWorkbench.js .ai/tasks/2026-06-04-agent-gate-artifact-linkage`
  - Result: `no trailing whitespace`.

## Frontend Build

- Command: `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline/web && npm run build"`
- Result: passed.
- Duration: `8m 49s`.
- Warning: existing Vite chunk-size warning for large vendor chunks over 500 kB.

## Browser QA

Target: `http://127.0.0.1:5173/worldline/agent`

- Page loaded with title `世界线 - Worldline`.
- Default Gate Run Panel included `gate:gate-permission`.
- Clicking `gate:gate-permission` focused the gate and opened a Focus Dossier titled `Permission risk`.
- Dossier chips after gate focus:
  - `Branch: 工具执行分支` disabled as passive context.
  - `Tool: worldline.plan_workflow` enabled.
  - `Tool: worldline.run_quality_gate` enabled.
  - `Artifact: Workflow plan` enabled.
- Clicking `Artifact: Workflow plan`:
  - Focused `artifact:artifact-workflow-plan`.
  - Switched Artifact Rail active scope to `Event4`.
  - Changed Focus Dossier title to `Workflow plan`.
- Clicking `Tool: worldline.plan_workflow` from the artifact dossier:
  - Focused `tool:tool-plan-workflow`.
  - Changed Focus Dossier title to `worldline.plan_workflow`.

## Screenshots

- `D:\dev\Worldline\.ai\tasks\2026-06-04-agent-gate-artifact-linkage\screenshots\gate-artifact-link-dossier.png`
- `D:\dev\Worldline\.ai\tasks\2026-06-04-agent-gate-artifact-linkage\screenshots\gate-artifact-link-focused-artifact.png`
