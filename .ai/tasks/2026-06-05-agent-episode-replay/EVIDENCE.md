# Evidence

## Static Checks

- `git diff --check -- web/src/data/worldline/agentWorkbench.js web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-episode-replay`
  - Result: passed with no whitespace errors.

## Build

- Windows `npm --prefix web run build`
  - Result: unavailable because `npm` is not installed on the Windows side.
- WSL Debian `npm --prefix web run build`
  - First run exceeded the outer 124s command timeout; the WSL process was allowed to finish and no build process remained.
  - Re-run result: passed.
  - Build time: 2m 39s.
  - Note: Vite kept the existing large chunk warning for G6/Ant Design/vendor bundles.

## Browser QA

- QA script: `.ai/tasks/2026-06-05-agent-episode-replay/qa-episode-replay.cjs`
- Target: `http://127.0.0.1:5173/worldline/agent`
- Method: headless Chrome CDP, 1600x1000 viewport.
- Assertions:
  - `episode:episode-tool` card is clickable.
  - Focus Dossier title contains `Episode Replay: executor`.
  - Dossier contains artifact, diff, and screenshot replay rows.
  - Clicking `Artifact: Workflow plan` opens the artifact Dossier.
  - Artifact Dossier contains the backlink `Episode: executor`.
- Result: passed.

## Screenshots

- `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-episode-replay\screenshots\episode-replay-dossier.png`
- `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-episode-replay\screenshots\episode-artifact-backlink.png`

## Cleanup

- Temporary Chrome profile was removed after verifying the resolved path was inside the task directory.
- No `npm run build` or `vite build` process remained after validation.
