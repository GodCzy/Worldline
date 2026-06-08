# Evidence

Date: 2026-06-08

## Initial Audit

- `KnowledgeGraphService.rebuild_graph()` already extracts entities, relationships, and temporal facts from evidence-bound chunks.
- `detect_temporal_conflicts()` already returns `status=needs_review` when two facts share subject, predicate, and date but have different objects.
- `KnowledgeGraphRepository.serialize_temporal_fact()` did not expose a direct `conflict_status` field before this slice.
- Existing live service tests cover the clean timeline path but not a reviewable conflict path.

## Completed Code

- `src/services/knowledge_graph_service.py`
  - Annotates extracted `TemporalFact` payloads with `fact_metadata.conflict`.
  - Adds `conflict_key` and `objects` to conflict reports.
  - Marks non-conflicting facts as `{"status": "clean"}`.
- `src/repositories/knowledge_graph_repository.py`
  - Serializes timeline facts with top-level `conflict_status`.
  - Keeps the full `metadata.conflict` object available for API/UI consumers.
- `test/test_worldline_live_services.py`
  - Adds a conflicting temporal fixture with two evidence-bound chunks.
  - Verifies rebuild conflict report, timeline serialization, and read-only Neo4j projection.

## Validation

Command:

```powershell
wsl -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && PYTHONPATH=. .venv/bin/pytest test/test_worldline_live_services.py -q -vv'
```

Result:

- `6 passed, 1 warning in 16.54s`
- Existing warning: SQLAlchemy `declarative_base()` deprecation.
- Existing environment warning after pytest: `RequestsDependencyWarning` for urllib3/chardet compatibility.

Command:

```powershell
git diff --check
```

Result:

- Exit code: `0`
- Git printed a CRLF normalization warning for `src/services/knowledge_graph_service.py`; no whitespace errors were reported.

## Contract Evidence

- `rebuild_graph("kb_conflict")` returns `conflicts.status=needs_review`.
- `/timeline` serialization exposes `conflict_status=needs_review` for both conflicting facts.
- `metadata.conflict.related_fact_ids` contains both fact ids.
- `metadata.conflict.evidence_ids` is non-empty.
- `build_neo4j_projection()` keeps `storage.write_enabled=false`.
- Projection `temporal_facts[].properties.conflict.status` is `needs_review`.

## Output Summary

- `D:\document\OutputMD\2026-06-08-Worldline-P3-2-Temporal-Conflict-Review.md`
