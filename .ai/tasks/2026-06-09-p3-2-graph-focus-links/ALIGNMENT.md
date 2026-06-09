# Alignment

Date: 2026-06-09

## Goal

Continue P3-2 by making graph, timeline, Wiki, and evidence references navigable instead of isolated counts.

This slice lets users open `/graph` with explicit focus query params, see which graph/timeline/evidence object is focused, and jump from Wiki citations or Worldline branch support into the graph review surface.

## Scope

- `web/src/views/GraphView.vue`
- `web/src/views/worldline/WorldlineWorkbenchView.vue`
- `web/src/components/WikiSection.vue`
- Reuse existing Worldline graph, timeline, evidence, and Wiki APIs.

## Non-goals

- No backend schema changes.
- No new graph visualization dependency.
- No direct Neo4j writes.
- No full `GraphCanvas` rewrite.
- No attempt to finish P3-6 quality replay in this slice.

## Acceptance Evidence

- `/graph?db_id=<kb>&entity_id=<id>` shows a focus banner and highlights the matching graph review entity when loaded.
- `/graph?db_id=<kb>&fact_id=<id>` shows the selected timeline fact and keeps conflict state visible.
- Wiki citation actions can open `/graph` with `evidence_id`.
- Worldline graph focus actions pass `entity_id` or `fact_id` into `/graph`.
- Desktop and `390x844` Browser QA have no page-level horizontal overflow and no console warnings/errors.
