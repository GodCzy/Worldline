# Evidence

Date: 2026-06-08

## Initial Audit

- `web/src/apis/worldline_api.js` already exposes graph entities, relationships, conflicts, Neo4j projection, rebuild, and timeline endpoints.
- `GraphView.vue` currently displays legacy unified graph canvas data from `/api/graph/subgraph`.
- P3-2 backend conflict metadata was already committed in `858aa88`.

## Implementation

- `web/src/views/GraphView.vue` now shows a compact `Worldline Graph Review` panel for non-Neo4j knowledge bases.
- The panel calls:
  - `GET /api/knowledge/databases/{db_id}/graph/entities`
  - `GET /api/knowledge/databases/{db_id}/graph/relationships`
  - `GET /api/knowledge/databases/{db_id}/graph/conflicts`
  - `GET /api/knowledge/databases/{db_id}/timeline`
  - `POST /api/knowledge/databases/{db_id}/graph/rebuild`
- The surface reports entity, relationship, timeline, and conflict counts, plus `needs_review` conflict state with fact ids and evidence ids.

## Browser QA

Temporary QA knowledge base:

- `db_id`: `kb_codex_graph_conflict_20260608143404`
- `file_id`: `file_ex_graph_conflict_20260608143404`
- API seed output: 8 entities, 23 relationships, 2 timeline facts, 1 `needs_review` conflict.
- Conflict fact ids included `tf_f67e47f3ae1a77f6b30c911ae55f839d` and `tf_c45f97474c5b64dfefef80e2a72a0382`.
- Evidence ids included `ev_723fa6db9c3e8ad39a9c6431ed111f7a` and `ev_90bd4c9203c4f240138b682e463be010`.

Screenshots:

- `D:\dev\Worldline\.ai\tasks\2026-06-08-p3-2-graph-conflict-surface\screenshots\graph-conflict-surface-desktop-1280x720.png`
- `D:\dev\Worldline\.ai\tasks\2026-06-08-p3-2-graph-conflict-surface\screenshots\graph-conflict-surface-mobile-390x844.png`

Rendered DOM checks:

- Desktop `1280x720`: panel visible, `Temporal conflicts need review` visible, `needs_review` visible, fact ids/evidence ids visible, timeline facts visible, `bodyScrollWidth == bodyClientWidth`, no browser console warnings/errors.
- Mobile `390x844`: panel visible, `needs_review` visible, fact ids/evidence ids visible, timeline facts visible, `bodyScrollWidth == bodyClientWidth`, no browser console warnings/errors, no overlap nodes reported by the DOM scan.

## Cleanup

Command:

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && docker compose exec -T -e PYTHONPATH=/app -e WORLDLINE_CONTENT_KB_DB_ID=kb_codex_graph_conflict_20260608143404 -e WORLDLINE_CONTENT_KB_ADMIN_LOGIN=codex_graph_admin api python3 - < .ai/tasks/2026-06-08-content-kb-full-chain/cleanup_content_kb_full_chain.py"
```

Result summary:

- `kb_deleted`: `true`
- `admin_deleted`: `true`

Follow-up database verification:

- `kb_exists`: `false`
- `admin_exists`: `true`
- `admin_is_deleted`: `1`

## Local Checks

- `docker compose ps`: API, graph, Milvus, etcd, MinIO, Postgres, and Redis were healthy before cleanup.
- `git diff --check`: passed; only Git's CRLF normalization warning for `web/src/views/GraphView.vue`.
- `wsl -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && /home/joy/.local/bin/npm --prefix web run build'`: passed in about 3m48s; Vite reported the existing large chunk warning.
- `wsl -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && /home/joy/.local/bin/npm run docs:build'`: passed in about 24s.
- Commit subject: `feat: surface graph conflict review`.
