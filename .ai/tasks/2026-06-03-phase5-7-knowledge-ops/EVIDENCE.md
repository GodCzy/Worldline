# Phase 5-7 Knowledge Ops Evidence

Updated: 2026-06-03

## Requirements

Source: `D:\document\Worldline\PROJECT_BOOK.md`, lines 192-206.

Phase 5:

- Entity/relationship extraction and evidence binding.
- `TemporalFact`, timeline, stale page detector.

Phase 6:

- Worldline MCP Server.
- LangGraph managed compile/rebuild/evaluation/graph update workflow shape.
- ARQ async dispatch boundary.

Phase 7:

- Golden set, coverage map, CI gate, failure replay.
- tracing, cost statistics, latency statistics, permission checks.

## ruff

Command:

```powershell
wsl -d Debian -- bash -lc "cd /tmp && uv run --no-project --index-url https://pypi.org/simple --with ruff ruff check /mnt/d/dev/Worldline/src/storage/postgres/models_knowledge.py /mnt/d/dev/Worldline/src/repositories/knowledge_graph_repository.py /mnt/d/dev/Worldline/src/services/knowledge_graph_service.py /mnt/d/dev/Worldline/src/services/worldline_agent_workflow_service.py /mnt/d/dev/Worldline/src/services/worldline_quality_gate_service.py /mnt/d/dev/Worldline/src/services/mcp_service.py /mnt/d/dev/Worldline/src/mcp/worldline_server.py /mnt/d/dev/Worldline/server/routers/knowledge_router.py /mnt/d/dev/Worldline/test/test_knowledge_object_models.py /mnt/d/dev/Worldline/test/test_worldline_phase5_7_services.py"
```

Result:

```text
All checks passed!
```

## pytest

Command:

```powershell
wsl -d Debian -- bash -lc "cd /tmp && WORLDLINE_SKIP_APP_INIT=1 SILICONFLOW_API_KEY=dummy TEST_USERNAME=phase57_admin TEST_PASSWORD=phase57_password PYTHONPATH=/mnt/d/dev/Worldline uv run --no-project --index-url https://pypi.org/simple --with pytest --with pytest-asyncio --with anyio --with httpx --with python-dotenv --with sqlalchemy --with aiofiles --with aiosqlite --with tomli --with tomli-w --with pydantic --with colorlog --with loguru python -m pytest /mnt/d/dev/Worldline/test/test_document_compiler.py /mnt/d/dev/Worldline/test/test_ragflow_like_chunking.py /mnt/d/dev/Worldline/test/test_knowledge_object_models.py /mnt/d/dev/Worldline/test/test_knowledge_object_repository.py /mnt/d/dev/Worldline/test/test_evidence_service.py /mnt/d/dev/Worldline/test/test_auto_wiki_service.py /mnt/d/dev/Worldline/test/test_worldline_phase5_7_services.py -q"
```

Result:

```text
37 passed, 1 warning in 6.13s
```

Warning:

- Existing SQLAlchemy `declarative_base()` deprecation in `src/storage/postgres/models_business.py`.

## PostgreSQL smoke

Temporary container:

```text
worldline-phase57-postgres
```

Result summary:

```json
{
  "counts": {
    "entities": 8,
    "golden_items": 16,
    "quality_gate_runs": 1,
    "relationships": 28,
    "temporal_facts": 1,
    "wiki_pages": 8,
    "workflow_runs": 1
  },
  "gate": {
    "evidence_accuracy": 1.0,
    "failure_replay_count": 0,
    "permission_checks_passed": true,
    "stale_page_count": 0,
    "status": "passed"
  },
  "golden_item_count": 16,
  "graph_counts": {
    "entities": 8,
    "relationships": 28,
    "temporal_facts": 1
  },
  "manifest_tools": [
    "worldline.compile_document",
    "worldline.rebuild_wiki",
    "worldline.update_graph",
    "worldline.run_quality_gate",
    "worldline.inspect_timeline"
  ],
  "stale_count": 0,
  "timeline_count": 1,
  "wiki_counts": {
    "document": 1,
    "glossary": 1,
    "home": 1,
    "topic": 5
  },
  "workflow": {
    "dispatch_backend": "arq",
    "orchestrator": "langgraph",
    "tool_count": 3
  }
}
```

Cleanup:

```text
docker rm -f worldline-phase57-postgres
```

Result:

```text
worldline-phase57-postgres
```

## Docs build

Command:

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm ci && npm run docs:build"
```

Result:

```text
build complete in 20.29s.
```

Notes:

- `npm ci` reported 4 moderate vulnerabilities.
- `npm audit fix` was not run to avoid unrelated lockfile changes.

## Final Repository Checks

### Cleanup

Removed temporary generated artifacts:

- `D:\dev\Worldline\node_modules`
- `D:\dev\Worldline\docs\.vitepress\dist`
- `D:\dev\Worldline\.pytest_cache`
- `D:\dev\Worldline\.ruff_cache`
- Python `__pycache__` directories under the project root

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
