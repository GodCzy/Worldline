# Frontend Style Unification Tasks

## Tasks

- [x] Audit frontend visual fragmentation.
- [x] Add shared Worldline design token stylesheet.
- [x] Import token stylesheet into the app CSS entry.
- [x] Restyle app shell and shared header.
- [x] Restyle graph page, graph canvas, and graph detail panel.
- [x] Normalize Worldline Hub and Workbench against shared tokens.
- [x] Normalize Worldline canvas, detail, evidence, graph focus, node, and scrubber components.
- [x] Run frontend build.
- [x] Run screenshot QA for `/worldline`, `/worldline/:themeId`, and `/graph`.
- [x] Record evidence and final summary.

## Verification Targets

- `pnpm --dir web build`
- Screenshot QA at 1920x1080, 1440x900, and 390x844.
- `git diff --check`
- `git status --short --branch`
