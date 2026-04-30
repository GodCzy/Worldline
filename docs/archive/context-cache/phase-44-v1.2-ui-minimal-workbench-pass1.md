# phase-44-v1.2-ui-minimal-workbench-pass1

## Date

- 2026-03-31

## Baseline

- start HEAD: `f1e4dc1 fix(worldline): reduce guest shell auth noise`
- prior stable conclusions:
  - worldline v1.2 first wave passed real-backend smoke once
  - guest-shell noise reduction pass was applied in frontend

## Phase Goal

- reduce workbench information density
- emphasize tree-shaped worldline as the primary visual
- keep nodes minimal and reveal detail on hover/click
- add a minimal embedded chat panel that reuses existing agent routes
- run the phase-2 UI optimization and bug-fix pass (frontend + public shell)

## Implemented UI Direction

- minimal node cards with short lines and tag hints
- hover tooltip for quick context
- click to update a compact detail panel
- chat panel embedded within the workbench via `embed=1` route mode
- reduced copy length in headers and stage metadata

## MCP / Workflow Reset

- Figma: layout and structure review for workbench and panel placement
- Playwright: repeatable smoke for `/worldline/poe` and `/worldline/unknown`
- Linear: phase task tracking (Phase 2 / Phase 3 / Phase 4)
- Notion: short acceptance checklist and phase summary logs
- Build Web Apps: quick component layout validation (non-authoritative)

## Phase Roadmap (Adjusted)

- Phase 2 (current): UI optimization + bug fix + guest-shell noise reduction
- Phase 3: further simplification + multi-theme visual adaptation
- Phase 4: module expansion + interaction protocol stabilization

## Validation Notes

- build completed after UI changes
- Playwright smoke confirmed:
  - `/worldline/poe` renders workbench and chat panel
  - `/worldline/unknown` renders fail-closed and no branch content
- backend health check failed during this round:
  - `GET http://127.0.0.1:5050/api/system/health` connection closed
- guest-mode should not trigger unnecessary auth requests from worldline interactions

## Phase Judgment

- current phase: `v1.2 UI minimalization + bug-fix pass`
- readiness for next phase: `pending re-smoke`
- main remaining gap before advancing:
  - confirm worldline smoke after UI changes
  - confirm embedded chat panel works with agent route reuse
