# Evidence

Date: 2026-06-08

## Initial Context

- API compose service is running and healthy on `http://127.0.0.1:5050`.
- Vite dev server responds on `http://127.0.0.1:5173`.
- Existing live service tests provide deterministic coverage for Wiki, graph, timeline, quality gate, and Worldline facade behavior.

## Validation Log

## Service Chain

Command:

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && docker compose exec -T -e PYTHONPATH=/app api python3 - < .ai/tasks/2026-06-08-content-kb-full-chain/run_content_kb_full_chain.py"
```

Result:

- `status=ok`
- `db_id=codex_content_kb_1780916790`
- `theme_id=codex-content-1780916790`
- `SourceAsset=1`
- `DocumentVersion=1`
- `DocumentNode=5`
- `EvidenceAnchor=5`
- `KnowledgeChunk=1`
- `WikiPage=11`
- `KnowledgeEntity=20`
- `KnowledgeRelationship=28`
- `TemporalFact=3`
- `GoldenSetItem=20`
- `QualityGateRun=1`
- `quality_gate_status=passed`
- `worldline_status=ready`
- `branch_count=3`
- First branch refs: `evidenceRefs=5`, `wikiRefs=5`, `entityRefs=6`, `timelineRefs=3`

## Backend Fix

The first real HTTP overview call failed with:

```text
GET /api/knowledge/databases/codex_content_kb_1780916790/worldline/overview failed: status=500 body={"detail":"查询 Worldline overview 失败: 'NoneType' object does not support item assignment"}
```

Root cause:

- `_ensure_database_exists()` calls `KnowledgeBaseManager.get_database_info()`.
- For this direct seeded KB, the Postgres metadata row exists but the underlying Milvus metadata layer can return `None`.
- `get_database_info()` then attempted to assign `additional_params` into `None`.

Fix:

- `src/knowledge/manager.py` now falls back to Postgres KB metadata when backend metadata is missing.
- `test/test_worldline_live_services.py` now covers this fallback.

Focused validation:

```text
2 passed, 3 deselected, 1 warning in 3.24s
```

## Real API Browser Context

Command:

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && WORLDLINE_CONTENT_KB_ADMIN_LOGIN=codex_kb_admin WORLDLINE_CONTENT_KB_DB_ID=codex_content_kb_1780916790 WORLDLINE_CONTENT_KB_THEME_ID=codex-content-1780916790 python3 .ai/tasks/2026-06-08-content-kb-full-chain/prepare_content_kb_browser_context.py"
```

Result:

- `status=ok`
- Temporary admin role: `superadmin`
- Theme visible in `/api/system/info`: `true`
- HTTP overview counts matched the service chain counts.
- HTTP generate result: `status=ready`, `branch_count=3`, `quality_status=passed`.

## Browser QA

URL:

```text
http://127.0.0.1:5173/worldline/codex-content-1780916790?theme=codex-content-1780916790&module=codex-content-1780916790&db_id=codex_content_kb_1780916790&knowledge_db_id=codex_content_kb_1780916790
```

Desktop QA:

- Viewport: `1280x720`
- Page displayed `Codex Content KB Live Chain`.
- Page displayed `已使用真实 Worldline facade 生成。`
- Page displayed `passed`, `真实知识库`, `3 条分支`, `Source / 5`.
- Page included evidence, wiki, graph/timeline, and quality-gate surfaces.
- Console error/warn logs: none.
- Screenshot: `D:\dev\Worldline\.ai\tasks\2026-06-08-content-kb-full-chain\screenshots\content-kb-full-chain-desktop-1280x720.jpg`

Mobile QA:

- Viewport: `390x844`
- `scrollWidth=390`, `clientWidth=390`, horizontal overflow: `false`
- Page displayed live theme, ready status, 3 branches, evidence, and gate information.
- Console error/warn logs: none.
- Screenshot: `D:\dev\Worldline\.ai\tasks\2026-06-08-content-kb-full-chain\screenshots\content-kb-full-chain-mobile-390x844.jpg`

## Cleanup

Cleanup result:

- `kb_deleted=true`
- `theme_deleted=true`
- `admin_deleted=true`

Verification:

- Temporary admin login returns `403`.
- Temporary theme visible in `/api/system/info`: `false`
- Temporary KB row exists: `false`
