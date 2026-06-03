# Worldline Frontend Style Unification Alignment

Date: 2026-06-03

## Goal

Unify the Worldline frontend UI so the app shell, Worldline workbench, and knowledge graph views share one premium dark visual language.

## User Intent

- UI style should feel unified, not visually fragmented between pages.
- Color palette should feel high-end, restrained, and consistent.
- Worldline should keep the black/cyan/gold luminous identity already chosen for Phase 5.

## Scope

- Add one shared Worldline design token layer.
- Apply that token layer to the app layout, shared header, Worldline Hub, Worldline Workbench, graph page, graph canvas, graph detail panel, and Worldline side panels.
- Preserve existing routes, API calls, stores, G6 graph behavior, Worldline generation contracts, and component structure.

## Out Of Scope

- No route changes.
- No backend or schema changes.
- No Three.js migration.
- No rewrite of existing mojibake text in this pass.
- No new package installation.

## Acceptance

- `/worldline`, `/worldline/:themeId`, and `/graph` should feel like one product surface.
- Graph page should no longer look like a light admin page.
- Shared shell and header should not create visual contrast against Worldline pages.
- Frontend build and screenshot QA should pass.
