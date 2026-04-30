# phase-48-playwright-permission-and-shell-smoke-path

## Date

- 2026-03-31

## Baseline

- start HEAD: `df6327d feat(worldline): adapt tree density for 3-5-8 branch readability`

## Playwright Permission Diagnosis

- MCP Playwright tool in current desktop session is unstable for this workspace:
  - earlier error: tried writing under `C:\Windows\System32\.playwright-mcp` (permission denied)
  - current error: `Target page, context or browser has been closed`
- conclusion:
  - this is not a worldline frontend bug.
  - it is a tooling-runtime issue in current MCP Playwright session state.

## Practical Resolution (No OS Privilege Escalation Needed)

- switched acceptance path to shell Playwright CLI (`npx playwright`).
- installed runtime browsers:
  - Chromium
  - WebKit
- produced smoke screenshots for:
  - desktop: `/worldline`, `/worldline/poe`, `/worldline/unknown`
  - fresh user-data dir (incognito-equivalent): `/worldline`
  - mobile (iPhone 12): `/worldline/poe`, `/worldline/unknown`

## Added Reusable Script

- `scripts/worldline-smoke-playwright.ps1`
- purpose:
  - run the same browser smoke path without depending on MCP Playwright tool state.
  - standardize screenshot outputs under `artifacts/playwright-smoke/`.

## Plugin / Connector Operation Rule (Controller)

- In this environment, Linear / Canva / Figma / Build Web Apps connectors are available.
- Controller can call them proactively when task scope matches; user does not need to trigger every call manually.
- for cross-thread stability, if the user wants guaranteed connector context on the next turn, keep mentions in prompt header.

## Phase Judgment

- current phase: `v1.2 acceptance with tooling hardening`
- readiness for next phase: `near-ready`
- main remaining gap:
  - finalize one complete QA sign-off record using shell Playwright evidence set and confirm v1.2 closure.

