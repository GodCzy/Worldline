# Design

## Strategy

Use one temporary live theme module to exercise theme detail and live Worldline routes. Public routes are opened directly. Admin routes are opened after logging in with a temporary superadmin account.

## Checks

For each route:

- Capture `1280x720` screenshot.
- Capture `390x844` screenshot.
- Record URL, visible route title, console error/warn count, `scrollWidth`, `clientWidth`, and representative overflow elements.

## Cleanup

The live theme and KB are created only for QA coverage and must be removed before this task is closed. Screenshots and evidence remain.
