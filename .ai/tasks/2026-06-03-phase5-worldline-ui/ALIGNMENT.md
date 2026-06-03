# Alignment

Date: 2026-06-03

## Goal

Complete Phase 5: rebuild the Worldline frontend workbench as the project-critical visual and operational surface.

## Scope

- `/worldline` command hub.
- `/worldline/:themeId` workbench.
- `/graph` Worldline graph-focus verification surface.
- Frontend store support for Phase 5 optional payload fields.
- Backend facade support for those optional fields.
- Screenshot verification for every required page and viewport.

## Product Rules

- The UI must feel like a real knowledge workbench, not a landing page.
- LLM Wiki and Evidence Graph are primary; RAG is only auxiliary.
- The visual language is dark, cyan/gold, left-to-right branch and convergence.
- Phase 5 uses Vue + SVG/Canvas/G6 only. No Three.js/TresJS.

## Acceptance

- `/worldline` launches a usable module without relying on stale demo content.
- `/worldline/phase5-preview` shows branches, evidence rail, timeline scrubber, graph focus, and Agent handoff.
- `/graph` can receive Worldline context through route query and render a focused graph page.
- Build, focused tests, docs build, docker config, and screenshot gates are recorded.
