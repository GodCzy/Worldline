# Phase 4 Auto-Wiki Evidence

Updated: 2026-06-03

## Requirements

Source: `D:\document\Worldline\PROJECT_BOOK.md`, lines 187-190.

- Auto-Wiki.
- Home page, document pages, topic pages, glossary page.
- Backlinks, freshness, local rebuild.

## Final Verification

### ruff

Command:

```powershell
wsl -d Debian -- bash -lc "cd /tmp && uv run --no-project --index-url https://pypi.org/simple --with ruff ruff check /mnt/d/dev/Worldline/src/storage/postgres/models_knowledge.py /mnt/d/dev/Worldline/src/repositories/wiki_repository.py /mnt/d/dev/Worldline/src/services/auto_wiki_service.py /mnt/d/dev/Worldline/server/routers/knowledge_router.py /mnt/d/dev/Worldline/test/test_knowledge_object_models.py /mnt/d/dev/Worldline/test/test_auto_wiki_service.py"
```

Result:

```text
All checks passed!
```

### pytest

Command:

```powershell
wsl -d Debian -- bash -lc "cd /tmp && WORLDLINE_SKIP_APP_INIT=1 SILICONFLOW_API_KEY=dummy TEST_USERNAME=phase4_admin TEST_PASSWORD=phase4_password PYTHONPATH=/mnt/d/dev/Worldline uv run --no-project --index-url https://pypi.org/simple --with pytest --with pytest-asyncio --with anyio --with httpx --with python-dotenv --with sqlalchemy --with aiofiles --with aiosqlite --with tomli --with tomli-w --with pydantic --with colorlog --with loguru python -m pytest /mnt/d/dev/Worldline/test/test_document_compiler.py /mnt/d/dev/Worldline/test/test_ragflow_like_chunking.py /mnt/d/dev/Worldline/test/test_knowledge_object_models.py /mnt/d/dev/Worldline/test/test_knowledge_object_repository.py /mnt/d/dev/Worldline/test/test_evidence_service.py /mnt/d/dev/Worldline/test/test_auto_wiki_service.py -q"
```

Result:

```text
32 passed, 1 warning in 6.60s
```

Warning:

- Existing SQLAlchemy `declarative_base()` deprecation in `src/storage/postgres/models_business.py`.

### PostgreSQL smoke

Temporary container:

```text
worldline-phase4-postgres
```

Result summary:

```json
{
  "rebuild_counts": {
    "document": 1,
    "glossary": 1,
    "home": 1,
    "topic": 5
  },
  "page_types": [
    "document",
    "glossary",
    "home",
    "topic"
  ],
  "doc_backlink_types": [
    "home",
    "topic",
    "topic",
    "topic",
    "topic",
    "topic",
    "glossary"
  ],
  "doc_evidence_count": 2,
  "doc_freshness": {
    "evidence_count": 2,
    "source_chunk_count": 1,
    "source_chunk_ids": [
      "file_phase4_smoke_chunk_0"
    ],
    "source_doc_version_ids": [
      "docv_c9351c770d7dfd19b762d3d3"
    ],
    "status": "fresh"
  },
  "local_counts": {
    "document": 1
  },
  "counts": {
    "knowledge_chunks": 1,
    "wiki_pages": 8
  }
}
```

Cleanup:

```text
docker rm -f worldline-phase4-postgres
```

Result:

```text
worldline-phase4-postgres
```

### Docs build

Command:

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm ci && npm run docs:build"
```

Result:

```text
build complete in 17.64s.
```

Notes:

- `npm ci` reported 4 moderate vulnerabilities.
- `npm audit fix` was not run to avoid unrelated lockfile changes.

## Final Repository Checks

### `git diff --check`

Command:

```powershell
git diff --check
```

Result:

```text
exit code 0
```

Notes:

- Git reported line-ending conversion warnings for existing Windows working-copy behavior.
- No whitespace errors were reported.

### Legacy content scan

Command:

```powershell
rg -n --hidden --glob '!**/.git/**' -i "<legacy-project-keywords>" .
```

Result:

```text
no matches
```

### Cleanup

Removed temporary generated artifacts:

- `D:\dev\Worldline\node_modules`
- `D:\dev\Worldline\docs\.vitepress\dist`
- `D:\dev\Worldline\docs\.vitepress\cache`
- `D:\dev\Worldline\.pytest_cache`
- `D:\dev\Worldline\.ruff_cache`
- Python `__pycache__` directories under the project root
