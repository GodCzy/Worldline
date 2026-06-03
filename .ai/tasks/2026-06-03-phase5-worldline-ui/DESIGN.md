# Design

## Surfaces

1. Hub: module selection, question launch, current protocol and quality status.
2. Workbench: worldline stage plus inspector column.
3. Graph: admin graph canvas with Worldline graph-focus banner.

## Components

- `WorldlineBranchCanvas`: SVG luminous branch stage.
- `WorldlineBranchNode`: accessible SVG node with hover/selected tooltip.
- `WorldlineBranchDetailPanel`: branch rationale, quality summary, next actions.
- `WorldlineEvidenceRail`: Evidence/Wiki/Graph/Time tabs.
- `WorldlineTimelineScrubber`: Source/Wiki/Graph/Gate snapshots.
- `WorldlineGraphFocusPanel`: entity, temporal, routeTrace, and graph handoff summary.

## Data Flow

Backend or adapter payload -> `worldlineStore.hydrate` -> selected branch computed refs -> canvas/inspector/evidence/scrubber/graph panels.

Live backend has priority. `phase5-preview` exists only for local UI verification and screenshots when no real knowledge bridge is available.

## Risk Controls

- Keep `/worldline/generate` compatible.
- Add optional fields only.
- Do not add frontend dependencies.
- Do not introduce Three.js.
- Do not write secrets or live tokens into screenshots or docs.
