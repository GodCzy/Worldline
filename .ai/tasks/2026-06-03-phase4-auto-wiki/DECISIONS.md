# Phase 4 Auto-Wiki Decisions

Updated: 2026-06-03

## D1. Build on Phase 3 chunks

Decision: Auto-Wiki reads `KnowledgeChunk` rows and their `evidence_ids`.

Reason: Phase 3 already established the evidence-bound chunk contract. Reusing it keeps Wiki pages traceable and avoids another ingestion path.

## D2. Deterministic first implementation

Decision: Use extractive deterministic generation for Phase 4.

Reason: The project book requires the Auto-Wiki layer and rebuild semantics, not LLM writing quality. Determinism makes smoke tests and local rebuild behavior auditable.

## D3. Local rebuild only touches document pages

Decision: `file_id` rebuild deletes and regenerates document pages for that file only.

Reason: This gives a safe local rebuild primitive. Global pages can be refreshed by a full rebuild and stale detection can be added in Phase 5.

## D4. Keep API admin-only

Decision: Rebuild and page query endpoints use the existing `get_admin_user` dependency.

Reason: Rebuild changes persisted derived pages and should not be exposed to ordinary users in the current backend contract.

## D5. Do not add MCP or frontend scope yet

Decision: Phase 4 stops at backend model, service, repository, and API contract.

Reason: The project instruction says MCP/tools should only be added when they reduce copy-paste or provide clear verification capability. Frontend and MCP exposure can be handled after the backend wiki contract is stable.
