# Evidence

## Static Checks

- `git diff --check -- web/src/data/worldline/agentWorkbench.js web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-skill-genome-dossier`
  - Result: passed with no whitespace errors.

## Build

- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
  - Result: passed.
  - Build time: 3m 32s.
  - Note: Vite kept the existing large chunk warning for G6/Ant Design/vendor bundles.

## Browser QA

- QA script: `.ai/tasks/2026-06-05-agent-skill-genome-dossier/qa-skill-genome.cjs`
- Target: `http://127.0.0.1:5173/worldline/agent`
- Method: headless Chrome CDP, 1600x1000 viewport.
- Assertions:
  - `skill:skill-agent-ledger-review` card is focusable and clickable.
  - Skill Dossier contains `PROMOTION`, criteria, gate, artifact, and episode links.
  - Clicking `Episode: executor` opens `Episode Replay: executor`.
- Result: passed.

## Screenshots

- `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-skill-genome-dossier\screenshots\skill-genome-dossier.png`
- `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-skill-genome-dossier\screenshots\skill-episode-link.png`

## Cleanup

- Temporary Chrome profile was removed after verifying the resolved path was inside the task directory.
- No `npm run build` or `vite build` process remained after validation.
