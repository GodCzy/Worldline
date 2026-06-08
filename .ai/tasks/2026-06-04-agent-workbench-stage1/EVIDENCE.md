# Evidence

## Initial State

- Active root: `D:\dev\Worldline`.
- Existing worktree was already dirty from earlier Worldline recovery and frontend/backend audit work.
- Stage 1 intentionally avoids schema migrations and persistent run ledger tables.

## Commands

- `git status --short --branch`: confirmed the branch is `codex/worldline-recovery-refactor` and the worktree was already dirty with earlier Worldline recovery/frontend-backend audit changes.
- `git diff --check`: passed. Git only reported existing CRLF replacement warnings for Windows-line-ending files.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`:
  - First attempt timed out after 244s and left a `vite build` process running.
  - The stale build process was terminated.
  - Final run passed in 4m 5s.
  - Vite still reports existing large chunk warnings for Ant Design Vue, G6, mindmap, ECharts, and markdown vendor bundles.
- In-app browser opened `http://127.0.0.1:5173/worldline/agent`; title was `世界线 - Worldline`.
- Browser screenshot QA:
  - `screenshots/agent-workbench-1440x900.png`
  - `screenshots/agent-workbench-390x844.png`

## Results

- Added `web/src/data/worldline/agentWorkbench.js` with a deterministic Stage 1 run payload and the future `WorldlineRun`, `WorldlineBranch`, `AgentEpisode`, and `SkillProposal` contract map.
- Added `web/src/views/worldline/WorldlineAgentWorkbenchView.vue`.
- Added `/worldline/agent` before the dynamic `/worldline/:themeId` route so the static Agent Workbench route is not swallowed by theme routing.
- Added a Worldline Hub `Agent` entry pointing to `/worldline/agent`.
- Added `worldlineRunApi` wrappers for future run-ledger endpoints under `/api/worldline/runs`.
- Browser DOM checks passed:
  - desktop 1440x900: workbench exists, SVG canvas exists, evidence rail exists, 4 branch buttons, 2 tool traces, 2 skill proposals, 4 gate items.
  - mobile 390x844: workbench exists, SVG canvas exists, evidence rail exists, 4 branch buttons, 2 tool traces, 2 skill proposals, 4 gate items.
- Desktop screenshot initially exposed a horizontal scrollbar; layout was tightened and recaptured. Final body horizontal overflow was `0`.

## Residual Risk

- This is a Stage 1 local run-ledger preview. Persistent backend tables, event streams, branch approval persistence, and skill proposal persistence are still future work.
- The new `worldlineRunApi` wrappers intentionally point at future endpoints that are not implemented yet; the current page does not depend on them.
- Existing Vite large chunk warnings remain a later bundle-splitting task.
- The broader worktree remains dirty from earlier Worldline work and was not cleaned or reverted in this pass.
