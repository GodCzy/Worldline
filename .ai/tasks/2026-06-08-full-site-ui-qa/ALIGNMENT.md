# Full Site UI QA

Date: 2026-06-08

## Goal

Run a full-site visual and responsive QA pass over the current Worldline frontend routes after the Run Ledger, Agent Workbench, Dashboard, and content-KB chain work.

## Routes

- `/`
- `/themes`
- `/themes/:themeId`
- `/worldline`
- `/worldline/:themeId`
- `/worldline/agent`
- `/graph`
- `/database`
- `/dashboard`
- `/extensions`

## Acceptance

- Desktop and mobile screenshots are captured for the route set or a justified representative subset.
- Mobile checks include `390x844` horizontal-overflow detection.
- Console error/warn logs are reviewed.
- Any blocking UI regressions are fixed or explicitly recorded.
- Temporary admin, theme module, and QA KB are removed after screenshots.
