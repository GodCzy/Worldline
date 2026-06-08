# Alignment

## Goal

Turn the Replay Export + MCP Readable work into an Agent handoff capsule that an external Agent can copy, inspect, and execute through the existing controlled Worldline MCP read boundary.

## Scope

- Add a compact handoff capsule section inside the existing `REPLAY EXPORT` panel.
- Reuse the current replay export artifact, selected event, focused dossier, ledger URI, and `worldline.inspect_run_artifacts` call.
- Include the handoff intent, MCP tool, args, write scope, quality gates, replay checkpoints, and rollback semantics.
- Keep this as a frontend/local preview feature; do not enable new writes or external tools.

## Non-Goals

- No new MCP server installation.
- No direct database or filesystem write MCP.
- No backend schema change.
- No replacement of existing Replay Export, Artifact Registry, or MCP Readable behavior.

## Acceptance

- The Agent workbench shows an `AGENT HANDOFF` section in Replay Export.
- Users can preview a structured handoff capsule and copy it.
- The capsule includes `worldline.inspect_run_artifacts`, the logical ledger URI, `include_content: false`, and a `write_scope: none` boundary.
- Frontend build and browser QA pass.
