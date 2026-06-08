# Decisions

## 2026-06-06

- Reuse `GET /api/worldline/runs/{run_id}/artifacts/read`; no backend route or schema changes.
- Treat `resource_detail_snapshot` as a replayable read-only artifact, not a restore/write operation.
- Keep the Registry row focus behavior and add a separate replay action so existing click behavior remains intact.
- Expose the replay read as a Last MCP Call with `include_content=true` so external Agent handoff can reproduce the same read boundary.
- Keep planned snapshot artifacts disabled for replay; only saved registry artifacts can be read from the ledger.
