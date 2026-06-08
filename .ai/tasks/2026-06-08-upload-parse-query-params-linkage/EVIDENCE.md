# Evidence

## Commands

- `python3 -m py_compile server/routers/knowledge_router.py test/api/test_knowledge_router.py`
- `docker compose exec -T api python -m py_compile /app/server/routers/knowledge_router.py /app/test/api/test_knowledge_router.py`
- `docker compose restart api`
- `docker compose exec -T -e PYTHONPATH=/app -e TEST_USERNAME=codex_p2_admin -e TEST_PASSWORD=... api pytest -q /app/test/api/test_knowledge_router.py -k 'query_params_persist_without_instance_metadata or admin_can_create_vector_db_with_reranker'`
- `python3 -m py_compile .ai/tasks/2026-06-08-upload-parse-query-params-linkage/run_upload_parse_query_params_linkage.py`
- `docker compose exec -T -e PYTHONPATH=/app -e TEST_USERNAME=codex_p2_admin -e TEST_PASSWORD=... api python - < .ai/tasks/2026-06-08-upload-parse-query-params-linkage/run_upload_parse_query_params_linkage.py`

## Results

- API container restarted and returned `healthy`.
- Focused live API pytest: `2 passed, 22 deselected, 1 warning in 3.10s`.
- Query params regression verified:
  - A Postgres-only KB row can call `PUT /api/knowledge/databases/{db_id}/query-params`.
  - Saved values persist under `knowledge_bases.query_params.options`.
  - `GET /query-params` merges saved `top_k=7` and `retrieval_content_scope=all` into the LightRAG option schema.
- Live upload/add/parse verification result:

```json
{
  "status": "ok",
  "db_id": "kb_ff5300d2ce2371d227cb5a301e3ab362",
  "task_id": "b1f3745238154ce9863d730e5aab6b34",
  "file_id": "file_8889be",
  "file_status": "parsed",
  "processing_checks": {
    "content_type": "file",
    "enable_ocr": "disable",
    "chunk_preset_id": "qa",
    "chunk_size": 321,
    "chunk_overlap": 33,
    "qa_separator": "\n@@\n",
    "chunk_token_num": 321,
    "overlapped_percent": 10,
    "delimiter": "\n@@\n",
    "has_document_compile": true
  }
}
```

- Cleanup:
  - Temporary KB row no longer exists after script cleanup.
  - Temporary superadmin `codex_p2_admin` was deleted.
  - Login as `codex_p2_admin` now returns `401`.

## Residual Risk

- Full document indexing is not forced by this P2-1 verification because it can invoke embedding and graph runtimes outside the parameter-persistence contract.
