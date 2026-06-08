# Design

## Data Contract

`TemporalFact.fact_metadata` gains an optional `conflict` object:

```json
{
  "status": "needs_review",
  "conflict_key": "subject|predicate|yyyy-mm-dd",
  "related_fact_ids": ["..."],
  "evidence_ids": ["..."],
  "object_count": 2
}
```

Facts without a detected conflict receive:

```json
{ "status": "clean" }
```

`KnowledgeGraphRepository.serialize_temporal_fact()` adds a compatible optional top-level `conflict_status` derived from `metadata.conflict.status`.

## Service Flow

1. `KnowledgeGraphService.rebuild_graph()` extracts facts from evidence-bound chunks.
2. The service detects conflicts before persistence.
3. The service annotates affected facts with review metadata.
4. Repository serialization exposes the status to `/timeline`.
5. `build_neo4j_projection()` already includes fact metadata in projection properties, so the conflict object is projected read-only.

## Risk

- Conflict status is metadata-only; no schema churn.
- Existing clients that ignore `conflict_status` continue to work.
- Quality gates already count conflicts through `detect_temporal_conflicts()`.
