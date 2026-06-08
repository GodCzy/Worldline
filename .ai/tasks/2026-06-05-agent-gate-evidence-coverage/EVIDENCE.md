# Gate Evidence Coverage Evidence

## Static Checks

- `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-gate-evidence-coverage`
  - Result: passed with no output.
- `rg -n "[ \t]+$" web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-gate-evidence-coverage`
  - Result: `no trailing whitespace`.

## Frontend Build

- Command: `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline/web && npm run build"`
- Result: passed.
- Final run duration: `3m 51s`.
- Warning: existing Vite chunk-size warning for large vendor chunks over 500 kB.

## Browser QA

Target: `http://127.0.0.1:5173/worldline/agent`

The Browser plugin runtime was not exposed in this resumed context, so QA used the same Chrome DevTools Protocol fallback as the previous stage. A temporary Chrome profile was removed after validation.

Verified chain:

- Focused `gate:gate-permission`.
  - Dossier title: `Permission risk`.
  - Dossier status: `review`.
  - Gate card support strip: `Evidence 1`, `Graph 1`, `Time 2`.
  - Dossier metadata:
    - `Support Source`: `工具执行分支`
    - `Evidence Links`: `1`
    - `Graph Links`: `1`
    - `Timeline Links`: `2`
  - Dossier support links enabled:
    - `Evidence: Controlled Agent workflow lanes`
    - `Graph: SkillProposal`
    - `Time: Stage 1 local ledger preview`
    - `Time: Persistent run ledger remains future work`
- Clicked `Evidence: Controlled Agent workflow lanes`.
  - Evidence Rail active tab: `Evidence 3`.
  - `evidence:ev-agent-workflow` focused and in viewport.
- Refocused `gate:gate-permission`, then clicked `Graph: SkillProposal`.
  - Evidence Rail active tab: `Graph 3`.
  - `graph:entity-skill-proposal` focused and in viewport.
- Refocused `gate:gate-permission`, then clicked `Time: Persistent run ledger remains future work`.
  - Evidence Rail active tab: `Time 2`.
  - `timeline:tf-stage2` focused and in viewport.

## Screenshots

- `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-gate-evidence-coverage\screenshots\gate-support-dossier.png`
- `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-gate-evidence-coverage\screenshots\gate-support-evidence-focus.png`
- `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-gate-evidence-coverage\screenshots\gate-support-graph-focus.png`
- `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-gate-evidence-coverage\screenshots\gate-support-timeline-focus.png`

## Correction Captured

Initial QA showed `gate-permission` incorrectly counted `Evidence 3 / Graph 3` because the helper merged explicit `branch.evidenceIds` with derived `branch.evidenceRefs`. The implementation was corrected to prefer explicit branch ids and only fall back to refs when ids are absent. Final QA confirms `Evidence 1 / Graph 1 / Time 2`.
