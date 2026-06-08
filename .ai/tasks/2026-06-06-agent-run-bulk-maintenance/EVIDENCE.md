# Evidence

## Planned Checks

- `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-06-agent-run-bulk-maintenance`
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- Browser QA on `http://127.0.0.1:5173/worldline/agent`

## Results

- PASS `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-06-agent-run-bulk-maintenance`
  - Result: no whitespace errors.
- PASS `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
  - Result: Vite build completed in `5m 10s` after final bulk bar layout adjustment.
  - Note: existing large chunk warnings remain for vendor bundles; no new build failure.
- PASS Browser QA with Chrome CDP:
  - Script: `.ai/tasks/2026-06-06-agent-run-bulk-maintenance/qa-run-bulk-maintenance-cdp.mjs`.
  - Target: `http://127.0.0.1:5173/worldline/agent`.
  - Captured archive requests:
    - `POST /api/worldline/runs/run-bulk-ready-one/archive`
    - `POST /api/worldline/runs/run-bulk-ready-two/archive`
  - Captured restore requests:
    - `POST /api/worldline/runs/run-bulk-ready-one/restore`
    - `POST /api/worldline/runs/run-bulk-ready-two/restore`
    - `POST /api/worldline/runs/run-bulk-archived/restore`
  - Verified UI state:
    - Bulk checkbox selection enables compatible action buttons.
    - Bulk archive archives only selected non-archived runs.
    - Bulk restore restores selected archived runs.
    - Selection is cleared after bulk restore.
    - Final rows show `ready` and `Archive` buttons.
  - Screenshot: `.ai/tasks/2026-06-06-agent-run-bulk-maintenance/screenshots/run-bulk-maintenance.png`.
  - Cleanup: isolated Chrome profile `.ai/tasks/2026-06-06-agent-run-bulk-maintenance/chrome-profile-cdp` removed after QA.

## Failure Notes

- Initial browser QA failed waiting for `Archived 2/2 selected runs.` because the script clicked multiple Vue checkboxes within one runtime task; Vue only observed one selected row. The QA script now waits between checkbox clicks, matching real operator interaction, and the rerun passed.
