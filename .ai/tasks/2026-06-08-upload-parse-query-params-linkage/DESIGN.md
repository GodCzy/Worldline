# Design

## Query Params

- Use `KnowledgeBaseRepository` as the durable source for `query_params`.
- Save values under `query_params.options`.
- Preserve compatibility with historical flat dict rows by reading flat keys when `options` is absent.
- Best-effort sync the running KB instance metadata when the row is present there, but do not fail if the metadata entry is missing.

## Upload And Parse

- The frontend sends add-document params through `documentApi.addDocuments`.
- `FileUploadModal.vue` includes upload/parse params and optional auto-index params in the request.
- `KnowledgeBase.add_file_record` resolves and persists chunk params.
- `KnowledgeBase.parse_file` carries the same params into the document compiler and persists the compile trace.

## Risk Controls

- Avoid forcing a full LightRAG index in this task because it may invoke embedding or graph runtime dependencies.
- Verify the index param path by code review and by the shared `update_file_params` persistence behavior used by both auto-index and manual index routes.
