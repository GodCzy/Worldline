# Phase 50 - Phase 3 kickoff mapping and Playwright MCP reinstall

## Baseline

- Previous stable point: `8498c72 fix(worldline): singleflight public info config for v1.2 signoff`
- `v1.2` is already formally closed
- This pass did **not** enter Phase 3 implementation
- This pass focused on:
  1. Phase 3 kickoff mapping and architecture boundaries
  2. Local Playwright MCP reinstall from the official GitHub repository

## Controller rule for this pass

Because the user explicitly requested early notice once the second phase was complete, the controller stopped at mapping/design and tooling repair. No Phase 3 frontend or backend implementation was started in this pass.

## First-wave subagent results

### system_mapper

Read and mapped the current worldline configuration spread across:

- `web/src/views/worldline/WorldlineHubView.vue`
- `web/src/views/worldline/WorldlineWorkbenchView.vue`
- `web/src/components/worldline/WorldlineBranchCanvas.vue`
- `web/src/stores/info.js`
- `web/src/stores/themeContext.js`
- `web/src/stores/worldlineContext.js`
- `web/src/data/worldline/index.js`
- `web/src/data/worldline/poeWorldlineAdapter.js`
- `web/src/data/poePhase1.js`
- `web/src/views/themes/ThemeDetailView.vue`
- `web/src/router/index.js`
- `web/src/layouts/AppLayout.vue`
- `web/src/main.js`

Key conclusion:

- Platform-fixed items are still scattered across Hub / Workbench / Canvas / store / adapter layers
- Theme-configurable items are still mostly embedded in `poeWorldlineAdapter.js` and `poePhase1.js`
- The minimum Phase 3 path should first pull platform-fixed configuration out of page components and split platform skeleton from theme strategy inside the worldline adapter layer

### product_architect

Produced the recommended configuration split:

- `platformWorldlineConfig`
- `themeWorldlineConfig`

Platform-fixed items should own:

- layout mode
- node kinds
- node sizes
- branch capacity
- edge density ceilings
- hover capacity
- panel structure
- fail-closed behavior
- guest redirect policy

Theme-configurable items should own:

- display name
- subtitle
- default question
- visual tokens
- semantic label dictionaries
- branch tone mapping
- asset references
- capability declarations

Hard boundary:

- themes must not override platform layout semantics, fallback behavior, routing semantics, guest redirect rules, or node/edge capacity rules

### qa_release_auditor

Phase 3 can start, but only as a structural extension round, not a visual polishing round.

Must-keep regressions:

- `/worldline`
- `/worldline/:themeId`
- `/worldline/unknown` fail-closed
- `/worldline/poe` workbench flow
- `/api/system/info`
- `/api/system/health`
- no renewed public-route auth noise

## Playwright MCP reinstall

### What was found

The previous local Codex config used:

```toml
[mcp_servers.playwright]
command = "npx"
args = ["@playwright/mcp@latest"]
```

This meant the MCP server was being launched from npm on demand, not from a locally pinned GitHub checkout.

### What was done locally

1. Cloned the official repository:
   - `https://github.com/microsoft/playwright-mcp.git`
   - local path: `C:/Users/godcz/.codex/vendor_imports/playwright-mcp`
2. Installed dependencies locally with `npm install`
3. Updated local Codex config:
   - `C:/Users/godcz/.codex/config.toml`
   - changed Playwright MCP command from `npx @playwright/mcp@latest` to local `node .../cli.js`
4. Removed old MCP browser profile state directories:
   - `C:/Users/godcz/AppData/Local/ms-playwright/mcp-chrome`
   - `C:/Users/godcz/AppData/Local/ms-playwright/mcp-chrome-15fda5f`

### Current limitation

The current active conversation still reported:

- `Target page, context or browser has been closed`

This indicates the live MCP tool process for the current session did not hot-reload to the new local server instance. The reinstall is complete on disk, but the current session likely needs a fresh Codex session or app restart before the new Playwright MCP configuration is actually used by the tool host.

## Phase judgment

- Current phase: `Phase 3 kickoff preparation`
- Readiness for next phase: `ready, but awaiting user-directed Phase 3 implementation order`
- Main remaining gap before advancing:
  - no structural blocker remains
  - user wants to arrange the next implementation step after seeing the kickoff mapping
