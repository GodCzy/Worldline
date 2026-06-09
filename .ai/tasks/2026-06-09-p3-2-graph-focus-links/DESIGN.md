# Design

## Query Contract

`/graph` accepts:

- `db_id` or `knowledge_db_id`
- `entity_id`
- `fact_id`
- `evidence_id`
- `focus_layer`
- `focus_label`

The route remains backward compatible. Missing focus params render the current graph review panel unchanged.

## GraphView Behavior

- Parse focus query params from Vue Router.
- Load Worldline entities, relationships, conflicts, and timeline as before.
- Compute focused entity, timeline fact, conflict, and evidence-linked records from the loaded review payload.
- Render a compact focus banner above metrics.
- Highlight matching entity/timeline/conflict cards.
- If the focused entity is present in the legacy canvas data, call `GraphCanvas.focusNode(id)` after render.

## Entry Points

- `WorldlineWorkbenchView` opens `/graph` with the first selected graph/timeline ref when available.
- `WorldlineGraphFocusPanel` entity chips emit the selected entity.
- `WikiSection` citation rows include an `Open graph` action with `evidence_id`.

## Risk

Graph data can be available in the Worldline review payload while the legacy `/api/graph/subgraph` canvas does not contain the same node id. In that case the focus banner and review cards still provide traceability, and canvas focus is best-effort.
