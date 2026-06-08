# Evidence

## Static Checks

- `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-run-diff-timeline`
  - Result: passed with no whitespace errors.

## Build

- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
  - Result: passed.
  - Build time: 2m 34s.
  - Note: Vite kept the existing large chunk warning for G6/Ant Design/vendor bundles.

## Browser QA

- QA script: `.ai/tasks/2026-06-05-agent-run-diff-timeline/qa-run-diff-timeline.cjs`
- Target: `http://127.0.0.1:5173/worldline/agent`
- Method: headless Chrome CDP, 1600x1000 viewport.
- Assertions:
  - Replay lane is visible.
  - Replay lane shows 4 steps.
  - Run Preview and Tool Pending steps are visible.
  - Tool and Artifact diff chips are visible.
  - Clicking Tool Pending synchronizes Event Detail.
  - Tool event status `approval_required` is visible after scrub selection.
- Result: passed.

## Screenshots

- `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-run-diff-timeline\screenshots\run-diff-timeline-lane.png`
- `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-run-diff-timeline\screenshots\run-diff-timeline-selected.png`

## Cleanup

- Temporary Chrome profile was removed after verifying the resolved path was inside the task directory.
- No `npm run build` or `vite build` process remained after validation.
