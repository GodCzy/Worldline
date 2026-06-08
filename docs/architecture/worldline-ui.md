# Worldline UI Architecture

Updated: 2026-06-03

## Position

Worldline UI is the primary product surface for the Evidence-backed LLM Wiki + Temporal Knowledge Graph OS. It is not a marketing landing page and not a generic RAG chat shell.

The first usable screen should expose work: sign in, inspect runtime status, add a custom knowledge module, launch a worldline, inspect evidence, scrub timeline snapshots, focus graph context, and hand a selected branch to an Agent.

## Visual Direction

- Dark operational console using the shared `--wl-*` token system.
- Cyan and gold luminous worldline bundles.
- Left-to-right root question, branching, inspection nodes, and convergence.
- SVG/Canvas/G6 first; no Three.js unless a later immersive view is explicitly scoped.
- Panels are compact work surfaces, not decorative nested cards.
- Home, theme hub, Worldline hub, workbench, graph, login, and sidebar must read as one visual system.

## Required Views

- `/`: command entry with runtime status, embedded login/initialization, module add entry, and Worldline launch.
- `/themes`: empty module registry with one `+` entry for future custom module creation.
- `/worldline`: command hub for real module selection, question launch, current status, and core surface checklist.
- `/worldline/:themeId`: full workbench with worldline stage, branch inspector, evidence rail, timeline scrubber, graph focus, and Agent handoff when a real live bridge exists.
- `/graph`: administrator graph surface that can receive Worldline route context and show focused graph data.

## Interaction Contract

- Unauthenticated Agent navigation routes to the home login panel, not a standalone login page.
- Hover/select on a branch highlights the branch path and updates the active inspector.
- Evidence rail must expose source uri, page, line, bbox, Wiki refs, entity refs, and timeline refs when present.
- Timeline scrubber switches Source/Wiki/Graph/Gate snapshots without changing the route.
- Agent handoff must preserve theme, module, scene, branch, focus, graph, and entry query context.
- Graph handoff must route to `/graph` with the same context.

## Data Contract

`worldlineStore.hydrate` remains compatible with older payloads and can consume these optional fields:

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

Live backend results take priority. Local adapters are not default product content and must not be treated as persisted knowledge sources.

## Screenshot Gates

Required viewports:

- `1920x1080`
- `1440x900`
- `390x844`

Required pages:

- `/`
- `/themes`
- `/worldline`
- `/agent` unauthenticated redirect to `/?login=1&redirect=/agent`
- authenticated sidebar state for Joy `superadmin`

Required states:

- Empty module state.
- Embedded login panel.
- Authenticated sidebar state.
- Worldline hub with no module.
- Mobile layout.
- Agent redirect behavior.
