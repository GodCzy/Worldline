# Phase 4 Auto-Wiki Alignment

Updated: 2026-06-03

## Goal

Implement Phase 4 from `D:\document\Worldline\PROJECT_BOOK.md`: Auto-Wiki for the Living Knowledge OS.

Authoritative scope:

- Auto-Wiki.
- Home page, document pages, topic pages, glossary page.
- Backlinks, freshness, local rebuild.

## Current Baseline

- Phase 3 is already committed at `b0dd251 feat(knowledge): add phase 3 evidence retrieval`.
- Phase 3 provides evidence-bound `KnowledgeChunk` data, evidence query APIs, and chunk-to-evidence persistence.
- Phase 4 builds on Phase 3 chunks and evidence anchors instead of creating a separate ingestion path.

## In Scope

- Add a persistent `wiki_pages` table contract.
- Generate deterministic Auto-Wiki pages from evidence-bound chunks.
- Persist page markdown, backlinks, evidence ids, freshness data, and source metadata.
- Expose admin-only rebuild and page query endpoints through the existing knowledge router.
- Support full database rebuild and single-file local document-page rebuild.
- Cover the model, service, repository, and PostgreSQL persistence path with tests or smoke checks.

## Out of Scope

- LLM-authored wiki synthesis.
- Entity graph extraction.
- Timeline or stale-page detector.
- Frontend Auto-Wiki UI.
- MCP exposure for wiki pages.
- Database migration tooling beyond model contract validation and table creation smoke.

## Acceptance Criteria

- Full rebuild produces at least one `home`, `document`, `topic`, and `glossary` page when evidence-bound chunks exist.
- Document pages include `evidence_ids`, `freshness.status=fresh`, source chunk counts, and source document version ids.
- Document pages have backlinks to the home page and glossary page.
- Topic pages backlink to relevant document pages.
- Local rebuild with `file_id` replaces only document pages for that file and does not remove global home/topic/glossary pages.
- API endpoints are protected by the existing admin dependency.
- Verification evidence is recorded in `EVIDENCE.md`.
