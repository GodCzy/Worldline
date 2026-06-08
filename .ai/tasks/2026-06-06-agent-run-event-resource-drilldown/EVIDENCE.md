# Evidence

## Planned Checks

- `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-06-agent-run-event-resource-drilldown`
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- Browser QA on `http://127.0.0.1:5173/worldline/agent`

## Results

- PASS `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-06-agent-run-event-resource-drilldown`
  - No whitespace or patch-format issues reported.
- PASS `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
  - Vite build completed in `4m 5s`.
  - Existing large chunk warnings remain for `vendor-g6`, `vendor-antdv`, and related bundles.
- PASS Browser QA with Chrome CDP:
  - Script: `.ai/tasks/2026-06-06-agent-run-event-resource-drilldown/qa-run-event-resource-drilldown-cdp.mjs`.
  - Target: `http://127.0.0.1:5173/worldline/agent`.
  - Mocked run list, run detail, event page, artifact list, and artifact read endpoint.
  - Captured resource request:
    - `GET /api/worldline/runs/run-event-resource-drilldown/artifacts/read?artifact_id=artifact-drilldown-001&include_content=true&limit=20`
  - Verified UI state:
    - Artifact event token is focused.
    - Focus Dossier shows `Drilldown Artifact`.
    - Resource Detail shows `worldline.inspect_run_artifacts`.
    - Resource Detail response includes `Artifact content loaded by resource drilldown.`
  - Screenshot: `.ai/tasks/2026-06-06-agent-run-event-resource-drilldown/screenshots/run-event-resource-drilldown.png`.
  - Cleanup: isolated Chrome profile `.ai/tasks/2026-06-06-agent-run-event-resource-drilldown/chrome-profile-cdp` removed after QA.
