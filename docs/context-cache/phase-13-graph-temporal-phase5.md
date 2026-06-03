# Phase 13 Graph And Temporal Phase 5

Updated: 2026-06-03

## Implemented

- `KnowledgeEntity`
- `KnowledgeRelationship`
- `TemporalFact`
- `KnowledgeGraphRepository`
- `KnowledgeGraphService`
- Admin endpoints:
  - `POST /knowledge/databases/{db_id}/graph/rebuild`
  - `GET /knowledge/databases/{db_id}/graph/entities`
  - `GET /knowledge/databases/{db_id}/graph/relationships`
  - `GET /knowledge/databases/{db_id}/timeline`
  - `GET /knowledge/databases/{db_id}/wiki/stale-pages`

## Behavior

- Entity and relationship extraction uses evidence-bound chunks.
- Relationships are deterministic `co_mentions` edges.
- Temporal facts are extracted from ISO-like dates in source text.
- Wiki stale detection compares saved `freshness` with current chunk/doc-version ids.

## Boundary

This phase does not sync to Neo4j and does not use LLM extraction yet.
