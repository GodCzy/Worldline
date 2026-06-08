# Evidence

## Planned Checks

- `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-06-agent-run-event-audit-filters`
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- Browser QA on `http://127.0.0.1:5173/worldline/agent`

## Results

- PASS `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-06-agent-run-event-audit-filters`
  - No whitespace or patch-format issues reported.
- PASS `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
  - Vite build completed in `3m 42s`.
  - Existing large chunk warnings remain for `vendor-g6`, `vendor-antdv`, and related bundles.
- PASS Browser QA with Chrome CDP:
  - Script: `.ai/tasks/2026-06-06-agent-run-event-audit-filters/qa-run-event-audit-filters-cdp.mjs`.
  - Target: `http://127.0.0.1:5173/worldline/agent`.
  - Mocked run list, run detail, event page, and artifact list.
  - Captured event request:
    - `GET /api/worldline/runs/run-event-audit-filters/events?limit=6&offset=0`
  - Verified UI state:
    - Initial audit status `6/6 matched`.
    - Search for `artifact-audit-target` narrows to `1/6 matched`.
    - Export JSON action reports `Event audit JSON prepared`.
    - Reset clears search.
    - Actor filter `reviewer` narrows to a single `Branch Approved` event.
  - Screenshot: `.ai/tasks/2026-06-06-agent-run-event-audit-filters/screenshots/run-event-audit-filters.png`.
  - Cleanup: isolated Chrome profile `.ai/tasks/2026-06-06-agent-run-event-audit-filters/chrome-profile-cdp` removed after QA.
