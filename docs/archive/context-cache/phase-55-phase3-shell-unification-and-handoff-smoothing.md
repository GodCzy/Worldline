# Phase 55 - Phase 3 shell unification and handoff smoothing

## Baseline

- Previous stable point: `4decde3` (working tree baseline before this patch round)
- User pain points targeted in this pass:
  1. worldline -> agent transition is abrupt
  2. login does not reliably auto-return to target page
  3. sidebar needs fixed expand/collapse behavior
  4. theme-module transitions feel like switching to another website

## Read-only subagent wave (actually executed)

This pass used real read-only subagents first, then controller-side implementation:

1. `system_mapper` (`019d47c2-274a-75e0-a26e-7f5c7788f58b`)
2. `product_architect` (`019d47c2-882e-7e00-bc1f-eb54215e2c76`)
3. `qa_release_auditor` (`019d47c2-578d-72c1-b2f1-54353baf0878`)

Converged P0 conclusions:

- root cause = shell mismatch (`/themes` on `BlankLayout`) + redirect handling inconsistency (`/login` fallback to `/`)
- first fixes should focus on platform layer:
  - route shell consistency
  - redirect priority
  - sidebar expand-state persistence
- then smooth module handoff language and context continuity

## What changed

### 1) Platform shell and routing continuity

File:

- `web/src/router/index.js`

Changes:

- moved `/themes` route from `BlankLayout` to `AppLayout`
- added redirect helper and updated `/login` authenticated guard:
  - authenticated user now consumes `sessionStorage.redirect` first
  - fallback to `/` only when no valid redirect exists

### 2) Login auto-return behavior

File:

- `web/src/views/LoginView.vue`

Changes:

- added `resolveRedirectPath()` to normalize redirect target
- on login success:
  - first jump to stored redirect target when available
  - fallback to `/agent`
- on mounted when already logged in:
  - also prioritize redirect target instead of always jumping to `/`

### 3) Fixed expandable sidebar with memory

File:

- `web/src/layouts/AppLayout.vue`

Changes:

- added fixed sidebar expand/collapse toggle
- persisted expand state with `localStorage` key `worldline_app_nav_expanded`
- expanded mode now shows nav labels (icon + text), collapsed mode keeps compact icon navigation
- updated sidebar width and nav item layout for smooth collapse/expand transition

### 4) Smoother worldline/theme -> agent handoff language

Files:

- `web/src/views/worldline/WorldlineWorkbenchView.vue`
- `web/src/views/themes/ThemeDetailView.vue`
- `web/src/views/themes/ThemeHubView.vue`
- `web/src/views/AgentView.vue`

Changes:

- worldline workbench:
  - changed CTA wording from “open full agent chat” to process-oriented “carry current branch to deep chat”
  - added handoff hint text in dialogue panel
  - writes handoff marker `sessionStorage.worldline_agent_handoff=1` before entering login/agent flow
- theme detail:
  - changed primary CTA wording to process-oriented flow language
  - added short continuity hint (“context will be carried to next step”)
  - also writes handoff marker before chat entry
- theme hub/detail:
  - removed page-level duplicated user info widget to reduce shell clutter after adopting `AppLayout`
- agent view:
  - detects handoff marker and renders compact context entry state
  - hides heavy recommendation strips/welcome panel in handoff mode
  - preserves a lightweight “you are in worldline deep-chat mode” guide
  - clears handoff marker when context is manually cleared

## Validation evidence

### Build

- `npm run build` passed

### Browser smoke (shell Playwright path)

- local dev server was started for verification on `http://127.0.0.1:5173`
- captured screenshots:
  - `artifacts/playwright-smoke/desktop-worldline.png`
  - `artifacts/playwright-smoke/desktop-worldline-poe.png`
  - `artifacts/playwright-smoke/desktop-worldline-unknown.png`
  - `artifacts/playwright-smoke/mobile-worldline-poe.png`
  - `artifacts/playwright-smoke/mobile-worldline-unknown.png`

### Runtime notes

- direct `docker compose ps` failed in this execution environment due Docker daemon pipe not available (`dockerDesktopLinuxEngine` not found).
- MCP Playwright in this session still returned `Transport closed`, so shell/browser-cli path was used instead.

## Phase judgment

- Current phase: `Phase 3 (front-end shell unification and flow smoothing)`
- Readiness for next phase: `not yet`
- Main remaining gap before advancing:
  - interaction-level acceptance with real backend session (especially login -> redirect -> agent continuity) should be re-run in a Docker-accessible environment with valid test credentials

