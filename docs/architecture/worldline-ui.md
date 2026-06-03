# Worldline UI Architecture

Updated: 2026-06-03

## Phase 5 Position

Worldline UI is the primary product surface for the Evidence-backed LLM Wiki + Temporal Knowledge Graph OS. It is not a marketing landing page and not a generic RAG chat shell.

The first usable screen should expose work: pick a knowledge module, launch a worldline, inspect evidence, scrub timeline snapshots, focus graph context, and hand the selected branch to an Agent.

## Visual Direction

- Dark operational console.
- Cyan and gold luminous worldline bundles.
- Left-to-right root question, branching, inspection nodes, and convergence.
- SVG first, no Three.js in Phase 5.
- Panels are compact work surfaces, not decorative nested cards.

## Required Views

- `/worldline`: command hub for module selection, question launch, current status, and Phase 5 surface checklist.
- `/worldline/:themeId`: full workbench with worldline stage, branch inspector, evidence rail, timeline scrubber, graph focus, and Agent handoff.
- `/graph`: administrator graph surface that can receive Worldline route context and show the focused graph loop.

## Interaction Contract

- Hover/select on a branch highlights the branch path and updates the active inspector.
- Evidence rail must expose source uri, page, line, bbox, Wiki refs, entity refs, and timeline refs when present.
- Timeline scrubber switches Source/Wiki/Graph/Gate snapshots without changing the route.
- Agent handoff must preserve theme, module, scene, branch, focus, graph, and entry query context.
- Graph handoff must route to `/graph` with the same context.

## Data Contract

`worldlineStore.hydrate` remains compatible with older payloads and can consume these optional Phase 5 fields:

- `knowledgeMode`
- `layers`
- `branches[].wikiRefs`
- `branches[].entityRefs`
- `branches[].timelineRefs`
- `branches[].quality`
- `snapshots`
- `quality`
- `routeTrace`
- `overview`

Live backend results take priority. `phase5-preview` is a local frontend validation adapter only; it must not be treated as a persisted knowledge source.

## Screenshot Gates

Required viewports:

- `1920x1080`
- `1440x900`
- `390x844`

Required pages:

- `/worldline`
- `/worldline/phase5-preview`
- `/graph?theme=phase5-preview&module=phase5-preview&scene=graph_timeline&version=worldline-phase5-preview&graph=phase5-graph-focus`

Required states:

- Empty or blocked state when no live bridge is available.
- Loading or fallback status during generation.
- With branches.
- Hover or selected branch.
- Evidence rail tab content.
- Timeline scrubber active state.
- Graph focus and Agent handoff controls.
