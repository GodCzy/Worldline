# P2-1 Upload, Parse, Query Params Linkage

Date: 2026-06-08

## Scope

- Verify that upload/add/parse processing params are passed from frontend payloads into backend `KnowledgeFile.processing_params`.
- Make query params durable through Postgres, with instance metadata used only as an optional live cache.
- Keep page behavior unchanged; this is a backend contract and evidence task.

## Acceptance

- `PUT /api/knowledge/databases/{db_id}/query-params` works even when the KB row exists in Postgres but is missing from backend instance metadata.
- `GET /api/knowledge/databases/{db_id}/query-params` merges saved Postgres options into the type-specific default option schema.
- Real upload/add/parse flow preserves chunk params in `knowledge_files.processing_params`.
- Temporary users, databases, and files are cleaned up after verification.
