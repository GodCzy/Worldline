# phase-45-v1.2-ui-visibility-and-runtime-check

## Date

- 2026-03-31

## Baseline

- start HEAD: `0e548a5 feat(worldline): minimal workbench UI and embedded chat`
- user feedback in this round: UI looked unchanged from previous version and runtime intermittently showed service connection failure.

## What Changed

- simplified workbench top interaction from heavy question bar to compact inline controls:
  - one-line input
  - one primary generate button
- removed right-side heavy information blocks in workbench view:
  - evidence rail removed from the main workbench page
  - next-step action block removed from the main workbench page
- kept only lightweight inspect surface:
  - compact branch detail panel
  - embedded chat panel

## Runtime Verification

- `npm run build` succeeded in `web/`.
- `docker compose restart web` executed and Vite HMR confirmed updates for `WorldlineWorkbenchView.vue`.
- proxy recheck after restart:
  - `GET http://127.0.0.1:5173/api/system/health` => 200
  - `GET http://127.0.0.1:5173/api/system/info` => 200
- `api-dev` logs show successful requests from `web-dev` after transient `ECONNREFUSED` window.

## Key Judgment

- the user-perceived “no difference” was primarily a visibility gap:
  - previous pass adjusted internals but visual hierarchy remained too close to old layout.
- this pass intentionally creates stronger visible deltas by removing dense side blocks and compressing top controls.

## Phase Judgment

- current phase: `v1.2 acceptance polishing (UI visibility + runtime stability checks)`
- readiness for next phase: `not yet`
- main remaining gap before advancing:
  - rerun browser-level acceptance screenshot/smoke in user environment and confirm the new compact layout is what the user now sees.

