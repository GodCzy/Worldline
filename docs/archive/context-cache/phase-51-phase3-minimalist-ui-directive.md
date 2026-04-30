# Phase 51 - Phase 3 minimalist UI directive

## Baseline

- Previous stable point: `6c1b08c docs(context-cache): record phase3 kickoff and playwright reinstall`
- `v1.2` remains formally closed
- Phase 3 implementation has still **not** started in this pass
- This pass refined the Phase 3 goal itself:
  - not only configuration cleanup
  - but a platform-wide minimalist UI and theme simplification pass

## User directive distilled

The Phase 3 target is now:

- interfaces should be concise and immediately scannable
- avoid large text blocks
- keep information layered and proportionate
- all pages and themes should move toward a restrained minimalist style
- preserve structure and platform/module boundaries while reducing presentation noise

## First-wave subagent conclusions

### system_mapper

Most impactful first-wave files for visible simplification:

1. `web/src/views/themes/ThemeDetailView.vue`
2. `web/src/views/worldline/WorldlineHubView.vue`
3. `web/src/views/worldline/WorldlineWorkbenchView.vue`
4. `web/src/components/worldline/WorldlineBranchCanvas.vue`
5. `web/src/data/worldline/poeWorldlineAdapter.js`

Reasoning:

- `ThemeDetailView.vue` is currently the heaviest text surface
- `WorldlineHubView.vue` still behaves too much like an explanation page rather than a decision-first entry page
- `WorldlineWorkbenchView.vue` still contains multiple explanatory blocks beyond the core stage flow
- `WorldlineBranchCanvas.vue` is the highest-frequency visual core and should be more restrained
- `poeWorldlineAdapter.js` is still a major source of long display copy and should be trimmed at the source

### product_architect

Phase 3 should be governed by two layers:

- `platformWorldlineConfig`
- `themeWorldlineConfig`

Additional minimalist design rule:

- platform controls information density ceilings
- themes may vary tone and labels, but not visual clutter budgets

Recommended platform-level restraint rules:

- keep one dominant visual job per section
- keep default copy short enough to scan in seconds
- prefer summary first, detail on hover/click/expansion
- keep badge and label counts low
- avoid repeating the same explanation in multiple regions

### qa_release_auditor

Phase 3 may simplify presentation, but must not simplify away structure.

Allowed:

- shorter subtitles
- fewer explanatory blocks
- merged low-value support panels
- reduced decorative or repetitive helper copy

Not allowed:

- weakening fail-closed behavior
- blurring module boundaries
- removing branch selection / continue generation / chat handoff
- causing public-route regressions
- reintroducing public auth noise or system info instability

## Minimalist implementation directive

Phase 3 first wave should **not** start from global layout refactors.

It should start from the heaviest information surfaces:

1. theme entry page
2. worldline hub
3. worldline workbench
4. branch stage heading density
5. theme copy generation source

## Page-level simplification intent

### Theme pages

- turn them from explanation-heavy detail pages into action-first module entry pages
- keep only:
  - module name
  - one short summary
  - 1-2 key capability highlights
  - clear entry actions
- push heavier details into expandable or deferred areas

### Worldline hub

- turn it into a selection-first workspace entry
- keep:
  - module selector
  - one concise question field
  - one clear primary action
- remove or compress repeated rule/explanation blocks

### Worldline workbench

- keep the stage dominant
- keep selected-branch summary minimal
- keep dialogue driver minimal
- move detail into hover/click/side-panel instead of persistent explanatory copy

### Stage

- stage heading and support copy should be minimal
- branch text should prioritize title + one short line
- detailed reasoning should not occupy the main visual rhythm by default

## MCP Playwright status

- Local reinstall from the official GitHub repository is complete on disk
- Current session still reports:
  - `Target page, context or browser has been closed`
- Practical conclusion:
  - browser verification remains available through shell Playwright
  - MCP Playwright likely needs a fresh Codex session or app restart before the new local server instance is actually used

## Phase judgment

- Current phase: `Phase 3 minimalist direction lock`
- Readiness for next phase: `ready`
- Main remaining gap before advancing:
  - the controller now has a stable simplification target and first-wave file list
  - the next step is user-directed approval of which Phase 3 slice to implement first
