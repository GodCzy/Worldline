# Evidence

## Static Checks

- `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-run-replay-manifest`
  - Result: passed with no whitespace errors.

## Build

- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
  - Result: passed.
  - Build time: 2m 38s.
  - Note: Vite kept the existing large chunk warning for G6/Ant Design/vendor bundles.

## Browser QA

- QA script: `.ai/tasks/2026-06-05-agent-run-replay-manifest/qa-run-replay-manifest.cjs`
- Target: `http://127.0.0.1:5173/worldline/agent`
- Method: headless Chrome CDP, 1600x1000 viewport.
- Assertions:
  - Run Preview event exposes `Open Replay Manifest`.
  - Run Manifest Dossier shows branch, episode, skill, evidence, tool, timeline, gate, and artifact counts.
  - Run Manifest links include Branch, Episode, Skill, Gate, and Artifact entries.
  - Clicking `Branch: 工具执行分支` opens Branch Dossier.
  - Branch Dossier contains branch metadata and links back to tools, gates, artifacts, episode, and skill.
- Result: passed.

## Screenshots

- `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-run-replay-manifest\screenshots\run-replay-manifest.png`
- `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-run-replay-manifest\screenshots\run-manifest-branch-dossier.png`

## Cleanup

- Temporary Chrome profile was removed after verifying the resolved path was inside the task directory.
- No `npm run build` or `vite build` process remained after validation.
