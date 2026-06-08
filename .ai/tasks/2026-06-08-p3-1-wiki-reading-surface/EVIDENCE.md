# Evidence

Date: 2026-06-08

## Completed Code

- `web/src/apis/worldline_api.js` added `getWikiPage(dbId, pageId)`.
- `web/src/components/WikiSection.vue` added the compact Wiki reading surface.
- `web/src/views/DataBaseInfoView.vue` added the `LLM Wiki` tab.
- `web/src/views/DataBaseInfoView.vue` added a narrow-screen stacked layout so the right knowledge panel and `LLM Wiki` tab are reachable at 390px.
- `web/src/components/WikiSection.vue` added long citation wrapping, Markdown wrapping, and responsive drawer width.

## Backend Contract Audit

The frontend reuses existing backend routes:

- `GET /api/knowledge/databases/{db_id}/wiki/pages`
- `GET /api/knowledge/databases/{db_id}/wiki/pages/{page_id}`
- `GET /api/knowledge/databases/{db_id}/wiki/stale-pages`
- `POST /api/knowledge/databases/{db_id}/wiki/rebuild`

Existing `test/test_auto_wiki_service.py` coverage includes:

- `review.status`
- `evidence_coverage.status`
- `citations[].source == EvidenceAnchor`
- supported claims
- open questions
- disputes
- RAG role
- backlinks

## Validation

### Focused Pytest

Command:

```powershell
wsl -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && PYTHONPATH=. .venv/bin/pytest test/test_auto_wiki_service.py -q -vv'
```

Result:

- `2 passed, 1 warning in 13.45s`
- Existing warning: SQLAlchemy `declarative_base()` deprecation.
- Existing environment warning after pytest: `RequestsDependencyWarning` for urllib3/chardet compatibility.

### Frontend Build

Command:

```powershell
wsl -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && /home/joy/.local/bin/npm --prefix web run build'
```

Result:

- Exit code: `0`
- Vite build completed: `built in 6m 11s`.
- Existing warning: several chunks are larger than 500 kB after minification.

### Diff Check

Command:

```powershell
git diff --check
```

Result:

- Exit code: `0`
- Git printed existing CRLF normalization warnings across the repository; no whitespace errors were reported.

## Browser QA

Temporary live data:

- `db_id=codex_content_kb_1780926720`
- `theme_id=codex-content-1780926720`
- `wiki_pages=11`
- `entities=20`
- `relationships=28`
- `temporal_facts=3`
- `quality_gate_status=passed`

Desktop:

- URL: `http://127.0.0.1:5173/database/codex_content_kb_1780926720`
- Viewport: default `1280x720`
- `LLM Wiki` tab loaded real data.
- Page showed `11 页面`, `11 支持主张`, `55 引用`, `0 stale`.
- Detail drawer showed `Wiki 页面详情`, Markdown content, review/coverage/freshness badges, and EvidenceAnchor ids.
- Console warning/error logs: `0`
- Screenshot: `D:\dev\Worldline\.ai\tasks\2026-06-08-p3-1-wiki-reading-surface\screenshots\wiki-reading-surface-desktop-1280x720.png`

Mobile:

- Viewport: `390x844`
- After responsive fix, active tab was `LLM Wiki`.
- `scrollWidth=390`, `clientWidth=390`, horizontal overflow: `false`.
- `WikiSection` mounted and displayed `证据化页面`, `11 页面`, `55 引用`, `主张`, `引用`, and `待审问题`.
- Screenshot: `D:\dev\Worldline\.ai\tasks\2026-06-08-p3-1-wiki-reading-surface\screenshots\wiki-reading-surface-mobile-390x844.png`

Mobile drawer:

- Drawer wrapper width: `390px`
- Markdown `clientWidth=329`, `scrollWidth=329`, horizontal overflow: `false`.
- Drawer showed `Wiki 页面详情`, Markdown content, and EvidenceAnchor ids.
- Screenshot: `D:\dev\Worldline\.ai\tasks\2026-06-08-p3-1-wiki-reading-surface\screenshots\wiki-reading-surface-mobile-drawer-390x844.png`

## Cleanup

Command:

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && WORLDLINE_CONTENT_KB_DB_ID='codex_content_kb_1780926720' WORLDLINE_CONTENT_KB_THEME_ID='codex-content-1780926720' WORLDLINE_CONTENT_KB_ADMIN_LOGIN='codex_wiki_admin' docker compose exec -T -e PYTHONPATH=/app -e WORLDLINE_CONTENT_KB_DB_ID='codex_content_kb_1780926720' -e WORLDLINE_CONTENT_KB_THEME_ID='codex-content-1780926720' -e WORLDLINE_CONTENT_KB_ADMIN_LOGIN='codex_wiki_admin' api python3 - < .ai/tasks/2026-06-08-content-kb-full-chain/cleanup_content_kb_full_chain.py"
```

Result:

- `kb_deleted=true`
- `theme_deleted=true`
- `admin_deleted=true`

Post-cleanup verification:

- Temporary admin login returned `403`.
- `/api/system/info` returned `containsTheme=False`.
- Postgres `knowledge_bases` count returned `0`.

## Output Summary

- `D:\document\OutputMD\2026-06-08-Worldline-P3-1-Wiki-Reading-Surface.md`
