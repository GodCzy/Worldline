# P3-3 Branch Canvas Completion Design

## Backend Contract

- `WorldlineWorkbenchService.generate_worldline()` remains the public payload source.
- Each branch now carries:
  - `routeTrace`: branch id, route path, support counts, support status, evidence-required policy, and hints.
  - `gateRefs`: latest quality gate id/status/failure count.
  - `quality.hints`: missing evidence/wiki/entity/timeline support hints.
- If no `EvidenceAnchor` refs are available, the service returns no branches and marks the payload as `needs_evidence`.

## Frontend Surfaces

- `WorldlineBranchCanvas.vue`: keep SVG branch canvas, add hover/focus preview and mobile-contained scroll behavior.
- `WorldlineBranchDetailPanel.vue`: display support status, hints, route trace, and gate refs in the existing inspector.
- `WorldlineGraphFocusPanel.vue`: read branch-level route trace and nested support counts.
- `WorldlineWorkbenchView.vue`: pass the active branch route trace to Graph Focus while keeping top-level trace as fallback.

## Tests

- Extend `test_worldline_live_services.py` for branch route trace and gate refs.
- Add an evidence-free generation test that proves default conclusions are blocked.

## Rollback

Revert this task's service, test, and Vue component changes. No migration rollback is required.
