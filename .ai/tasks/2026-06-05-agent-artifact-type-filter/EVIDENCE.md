# Evidence

## Static Checks

- Command: `rg -n "artifactRegistryFilter|artifactRegistryItems|filteredArtifactRegistryItems|artifactRegistryFilters|registryArtifactTypeLabel|registryState|registry-filter|registry-artifact|data-artifact-registry" web/src/views/worldline/WorldlineAgentWorkbenchView.vue`
- Result: found the registry state, merged item list, filters, labels, planned/saved state, template marker, and styles.
- Command: `git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-artifact-type-filter`
- Result: passed.

## Frontend Build

- Command: `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm --prefix web run build"`
- Result: passed.
- Note: Vite still reports existing vendor large chunk warnings for bundles such as `vendor-antdv`, `vendor-g6`, and `vendor-mindmap`; this stage did not change code splitting.

## Browser QA

- Script: `.ai/tasks/2026-06-05-agent-artifact-type-filter/qa-artifact-type-filter.cjs`
- URL: `http://127.0.0.1:5173/worldline/agent`
- Result: passed after making the `Registry` assertion case-insensitive.
- First run failure recorded: browser `innerText` rendered `Registry` as `REGISTRY` because of style transformation, while the UI was already present and correct.
- Assertions covered:
  - Registry is visible in local preview.
  - Planned replay artifact appears as `Replay / planned`.
  - Planned handoff artifact appears as `Handoff / planned`.
  - `Handoff` filter hides the replay artifact and shows the handoff artifact.
  - `Replay` filter hides the handoff artifact and shows the replay artifact.
- Screenshots:
  - `.ai/tasks/2026-06-05-agent-artifact-type-filter/screenshots/artifact-registry-handoff-filter.png`
  - `.ai/tasks/2026-06-05-agent-artifact-type-filter/screenshots/artifact-registry-replay-filter.png`

## Visual QA

- Handoff screenshot checked: Registry shows only `Agent Handoff: Run Preview` with `Handoff / planned`.
- Replay screenshot checked: Registry shows only `Replay Export: Agent Workbench Stage 1` with `Replay / planned`.
- No incoherent overlap was observed across left rail, central worldline/timeline area, and right replay rail.

## Temporary Browser Cleanup

- Started a dedicated Chrome CDP instance on port `9347` with task-local profile `chrome-profile`.
- Stopped Chrome processes whose command line referenced that profile.
- Removed the task-local `chrome-profile`; final existence check returned `False`.
