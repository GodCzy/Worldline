# Design

## UI

Add a compact panel below the graph state/theme banners:

- Header: `Worldline Graph Review`
- Actions: refresh, rebuild graph
- Metrics: entities, relationships, timeline, conflicts
- Conflict list: subject, predicate, date, object count, fact ids, evidence ids
- Timeline list: occurred date, subject, conflict status, evidence count

The panel is unframed page content with a restrained dark console style. It should wrap on mobile rather than forcing horizontal scroll.

## API

Reuse:

- `GET /api/knowledge/databases/{db_id}/graph/entities`
- `GET /api/knowledge/databases/{db_id}/graph/relationships`
- `GET /api/knowledge/databases/{db_id}/graph/conflicts`
- `GET /api/knowledge/databases/{db_id}/timeline`
- `POST /api/knowledge/databases/{db_id}/graph/rebuild`

## State

`GraphView.vue` keeps `temporalReview` local state:

- `loading`
- `rebuilding`
- `error`
- `entities`
- `relationships`
- `conflicts`
- `timeline`

## Risk

The existing unified graph canvas still uses `/api/graph/subgraph`. This slice adds a Worldline graph review surface without replacing the existing graph canvas.
