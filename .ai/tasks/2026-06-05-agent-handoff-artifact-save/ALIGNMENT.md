# Alignment

## Goal

Make the Agent handoff capsule persistable through the existing Worldline run ledger artifact registry so it can later be read by external Agents through `worldline.inspect_run_artifacts`.

## Scope

- Add a `Save Handoff` action to the existing `AGENT HANDOFF` panel.
- Serialize the current handoff capsule as an artifact kind `agent_handoff_capsule`.
- Reuse the existing `/api/worldline/runs/{run_id}/artifacts` frontend API.
- Keep backend/admin write gating unchanged.

## Non-Goals

- No backend route change.
- No database schema change.
- No new MCP tool.
- No automatic external Agent execution.

## Acceptance

- Local preview shows `Save Handoff`, disabled when admin ledger access is unavailable.
- The payload uses `kind: agent_handoff_capsule` and preserves `write_scope: none`.
- Frontend build and browser QA pass.
- Evidence and OutputMD summary are written.
