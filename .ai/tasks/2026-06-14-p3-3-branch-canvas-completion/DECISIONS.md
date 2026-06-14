# P3-3 Branch Canvas Completion Decisions

## Evidence Required

Worldline branches must not be generated when there are no `EvidenceAnchor` refs. The payload returns `needs_evidence` instead of a fabricated branch.

## Optional Fields Only

P3-3 adds `routeTrace`, `gateRefs`, and support hints as optional branch fields. Existing top-level fields and store hydration remain intact.

## Compact UI

The Inspector receives the new details because it is already the compact review surface. No new page or broad layout is introduced.
