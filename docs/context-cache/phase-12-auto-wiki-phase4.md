# Phase 12 Auto-Wiki Phase 4

Updated: 2026-06-03

## Phase

This pass implements Phase 4 from the Worldline project book: Auto-Wiki.

Phase 3 baseline:

- Commit: `b0dd251 feat(knowledge): add phase 3 evidence retrieval`
- Phase 3 established evidence-bound chunks and evidence query APIs.

## Implemented

- `WikiPage`
  - Persistent Auto-Wiki page table.
  - Stores page type, slug, markdown, backlinks, evidence ids, freshness, and metadata.
- `WikiRepository`
  - Upserts generated pages.
  - Lists and fetches pages.
  - Loads source chunks joined with source file metadata.
  - Deletes pages by database or local rebuild scope.
- `AutoWikiService`
  - Full database rebuild.
  - Single-file local rebuild for document pages.
  - Deterministic document, topic, glossary, and home pages.
  - Backlinks and freshness payloads.
- `knowledge_router`
  - `POST /knowledge/databases/{db_id}/wiki/rebuild`
  - `GET /knowledge/databases/{db_id}/wiki/pages`
  - `GET /knowledge/databases/{db_id}/wiki/pages/{page_id}`

## Verification Plan

Final validation for this pass:

- ruff on changed Python files.
- pytest on document compiler, chunking, knowledge object, evidence, and Auto-Wiki tests.
- PostgreSQL smoke against a temporary container.
- VitePress docs build.
- `git diff --check`.
- Legacy content scan.

## Boundaries

Still not included:

- LLM-authored wiki synthesis.
- Frontend Auto-Wiki UI.
- MCP tools exposing wiki pages.
- Semantic entity graph extraction.
- Timeline or stale-page detector.

## Next Phase Candidate

Phase 5 can use `WikiPage.freshness` as the basis for stale page detection, entity graph links, temporal facts, and graph/wiki dependency tracking.
