# Evidence

## Planned Checks

- `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-06-agent-run-selector-pagination`
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- Browser QA on `http://127.0.0.1:5173/worldline/agent`

## Results

- PASS `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-06-agent-run-selector-pagination`
  - Result: no whitespace errors.
- PASS `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
  - Result: Vite build completed in `3m 40s` after the final loaded-window refresh fix.
  - Note: existing large chunk warnings remain for vendor bundles; no new build failure.
- PASS Browser QA with Chrome CDP:
  - Script: `.ai/tasks/2026-06-06-agent-run-selector-pagination/qa-run-selector-pagination-cdp.mjs`.
  - Target: `http://127.0.0.1:5173/worldline/agent`.
  - Captured pagination requests:
    - `GET /api/worldline/runs?limit=8&offset=0`
    - `GET /api/worldline/runs?limit=8&offset=8`
  - Captured page-two maintenance request:
    - `POST /api/worldline/runs/run-page-09/archive`
  - Captured loaded-window refresh:
    - `GET /api/worldline/runs?limit=10&offset=0`
  - Verified UI state:
    - First page loads 8 rows.
    - Load More appends 2 rows for a total of 10/10.
    - Page-two row `run-page-09` can be selected and archived.
    - The list preserves the loaded 10-row window after the page-two maintenance action.
    - Selection is cleared after archive.
    - Load More is disabled after all rows are loaded.
  - Screenshot: `.ai/tasks/2026-06-06-agent-run-selector-pagination/screenshots/run-selector-pagination.png`.
  - Cleanup: isolated Chrome profile `.ai/tasks/2026-06-06-agent-run-selector-pagination/chrome-profile-cdp` removed after QA.

## Failure Notes

- Initial browser QA failed waiting for `run-page-09 / archived` because page-two maintenance triggered a first-page refresh, removing the page-two row from the selector. Fixed by adding `refreshLoadedLedgerRuns()`, which reloads the current loaded window with `limit=<loaded_count>&offset=0`.
- A subsequent QA retry failed because the previous Chrome CDP port was no longer listening. Restarted the isolated Chrome profile and reran the same QA successfully.
