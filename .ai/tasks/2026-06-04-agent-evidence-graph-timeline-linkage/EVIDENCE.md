# Evidence Graph Timeline Linkage Evidence

## Static Checks

- `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue web/src/components/worldline/WorldlineEvidenceRail.vue .ai/tasks/2026-06-04-agent-evidence-graph-timeline-linkage`
  - Result: passed with no output.
- `rg -n "[ \t]+$" web/src/views/worldline/WorldlineAgentWorkbenchView.vue web/src/components/worldline/WorldlineEvidenceRail.vue .ai/tasks/2026-06-04-agent-evidence-graph-timeline-linkage`
  - Result: `no trailing whitespace`.

## Frontend Build

- Command: `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline/web && npm run build"`
- Result: passed.
- Final run duration: `5m 5s`.
- Warning: existing Vite chunk-size warning for large vendor chunks over 500 kB.

## Runtime QA

Primary Browser plugin execution could not be reused in the resumed context because `node_repl` was not exposed after tool discovery. Fallback used a local headless Chrome DevTools Protocol session against the same `http://127.0.0.1:5173/worldline/agent` dev server.

- Dev server:
  - Started hidden through WSL on `http://127.0.0.1:5173/`.
  - Log: `/tmp/worldline-vite-linkage.log`.
- Chrome CDP:
  - Version endpoint responded on `http://127.0.0.1:9223/json/version`.
  - Temporary Chrome profile was removed after QA.

Verified interaction chain:

- Clicked `evidence:ev-worldline-contract`.
  - Dossier title: `Worldline backend contract`.
  - Active rail tab: `Evidence 3`.
  - Evidence item focused: `true`.
  - Dossier links enabled:
    - `Graph: WorldlineRun`
    - `Time: Persistent run ledger remains future work`
- Clicked `Graph: WorldlineRun`.
  - Dossier title: `WorldlineRun`.
  - Active rail tab: `Graph 3`.
  - Graph item focused: `true`.
  - Graph target was in the Evidence Rail viewport.
  - Dossier backlink enabled: `Evidence: Worldline backend contract`.
- Clicked `Evidence: Worldline backend contract`.
  - Active rail tab returned to `Evidence 3`.
  - Evidence item focused: `true`.
- Clicked `Time: Persistent run ledger remains future work`.
  - Dossier title: `Persistent run ledger remains future work`.
  - Active rail tab: `Time 2`.
  - Timeline item focused: `true`.
  - Timeline target was in the Evidence Rail viewport, not the Time Scrubber duplicate target.
  - Dossier backlink enabled: `Evidence: Worldline backend contract`.
- Clicked the timeline Evidence backlink.
  - Active rail tab returned to `Evidence 3`.
  - Evidence item focused: `true`.

## Screenshots

- `D:\dev\Worldline\.ai\tasks\2026-06-04-agent-evidence-graph-timeline-linkage\screenshots\evidence-dossier-links.png`
- `D:\dev\Worldline\.ai\tasks\2026-06-04-agent-evidence-graph-timeline-linkage\screenshots\graph-dossier-backlink.png`
- `D:\dev\Worldline\.ai\tasks\2026-06-04-agent-evidence-graph-timeline-linkage\screenshots\timeline-dossier-backlink.png`
