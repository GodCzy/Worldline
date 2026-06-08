# Alignment

## Goal

Surface the new read-only MCP artifact inspection path inside the Agent Workbench Replay Export panel.

## Scope

- Show `worldline.inspect_run_artifacts` in the frontend.
- Show the logical artifact URI derived from the run ledger artifact id.
- Show compact MCP call arguments for external Agent use.
- Add a copy action for the MCP read call.
- Preserve local preview when backend/admin access is unavailable.

## Out Of Scope

- No backend route changes.
- No MCP contract changes.
- No direct database or filesystem MCP.
- No unrelated UI refactor.

## Acceptance

- Replay Export panel includes a visible `MCP READABLE` block.
- The block displays tool name, artifact URI, status, and copy action.
- Local non-admin preview clearly says artifact must be saved before external Agents can read it.
- Frontend build and Chrome CDP QA pass.
