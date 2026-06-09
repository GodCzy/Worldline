# Alignment

Date: 2026-06-08

## Goal

Advance P3-2 by exposing Temporal Knowledge Graph conflict state in the frontend graph console.

This slice connects `/graph?db_id=<kb>` to the Worldline graph/timeline APIs so users can see whether graph facts are clean or need review.

## Scope

- `web/src/views/GraphView.vue`
- Reuse existing `worldlineApi` graph and timeline endpoints.
- Browser QA at default desktop and `390x844`.

## Non-goals

- No new graph visualization dependency.
- No direct Neo4j writes.
- No schema or backend API changes in this slice.
- No large redesign of `GraphCanvas`.

## Acceptance Evidence

- `/graph?db_id=<temporary_kb>` shows a `Worldline Graph Review` panel.
- Panel shows entities, relationships, timeline facts, and conflict count.
- When conflicts exist, panel exposes `needs_review`, fact ids, evidence ids, and related timeline facts.
- Desktop and `390x844` screenshots have no page-level horizontal overflow.
