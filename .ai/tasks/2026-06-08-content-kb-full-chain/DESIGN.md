# Design

## Live Data Strategy

The task seeds one deterministic Markdown-like document directly through the same compiler persistence boundary used by the unit tests:

- `KnowledgeBase` and `KnowledgeFile` create the KB/file metadata.
- `KnowledgeObjectRepository.persist_compiled_document()` creates `SourceAsset`, `DocumentVersion`, `DocumentNode`, and `EvidenceAnchor`.
- `KnowledgeObjectRepository.bind_chunks_to_latest_evidence()` creates `KnowledgeChunk`.
- `AutoWikiService.rebuild_wiki()` creates `WikiPage`.
- `KnowledgeGraphService.rebuild_graph()` creates `KnowledgeEntity`, `KnowledgeRelationship`, and `TemporalFact`.
- `WorldlineQualityGateService.build_golden_set()` and `run_gate()` create `GoldenSetItem` and `QualityGateRun`.
- `WorldlineWorkbenchService.build_overview()` and `generate_worldline()` verify the live facade contract.

## Browser Strategy

Create a temporary custom theme module that points to the temporary KB. The browser route uses:

`/worldline/{theme_id}?theme={theme_id}&module={theme_id}&db_id={db_id}&knowledge_db_id={db_id}`

This exercises the real theme-module bridge and live Worldline API path instead of falling back to local preview data.

## Cleanup

Cleanup removes data in this order:

1. Delete the custom theme module through `/api/system/themes/{theme_id}`.
2. Delete the temporary KB row; PostgreSQL cascade removes related knowledge objects.
3. Soft-delete the temporary admin user.

Screenshots and task evidence stay in the task directory.
