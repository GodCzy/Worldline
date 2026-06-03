# Frontend Style Unification Design

## Visual Direction

Worldline uses a dark obsidian base with restrained cyan and gold accents:

- Obsidian background for the app shell and workbench.
- Cyan for structure, graph energy, borders, and secondary focus.
- Gold for primary action, active branch, time focus, and evidence emphasis.
- Soft blue-white text for readable information density.

## Token Layer

The shared token file is:

`web/src/assets/css/worldline-design.css`

It defines:

- `--wl-bg-*` for background strata.
- `--wl-page-bg` for common full-page luminous background.
- `--wl-panel`, `--wl-panel-soft`, `--wl-border`, `--wl-border-strong`.
- `--wl-cyan`, `--wl-gold`, RGB variants, text and muted text variables.
- `--wl-graph-node-*` and `--wl-graph-edge` for G6.

## Application Surface

- `AppLayout.vue` uses the same dark shell and active nav accents.
- `HeaderComponent.vue` uses a glass dark header with the same border and text palette.
- `GraphView.vue` becomes a dark graph workbench instead of a light admin surface.
- `GraphCanvas.vue` uses the token palette for G6 nodes, labels, edges, and stats.
- Worldline components use the same token set for panels, chips, buttons, evidence, and time scrubber.

## Design Constraints

- Cards stay at 8px radius or less.
- No decorative gradient orbs are introduced.
- The first screen remains the usable workbench, not a marketing hero.
- Text sizes stay stable and do not scale with viewport width.
- No feature behavior is changed during this visual pass.
