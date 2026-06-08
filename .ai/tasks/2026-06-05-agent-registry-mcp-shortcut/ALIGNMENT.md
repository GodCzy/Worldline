# Alignment

## Goal

Let each Replay Export Registry artifact expose its own read-only MCP shortcut so external Agents can copy the exact `worldline.inspect_run_artifacts` call for replay and handoff artifacts.

## Scope

- Add an item-level `Copy MCP` action to Registry rows.
- Build the URI from each artifact id and run id.
- Keep `include_content: false` as the safe default.
- Preserve existing Registry filters and focus behavior.

## Non-Goals

- No new MCP tool.
- No backend route or schema change.
- No direct external Agent execution.
- No change to admin-gated save behavior.

## Acceptance

- Registry rows show a compact `Copy MCP` action.
- Copy payload includes `worldline.inspect_run_artifacts`, the artifact-specific URI, and `include_content: false`.
- Browser QA verifies both Replay and Handoff filtered rows expose the shortcut.
- Build, whitespace check, screenshots, and OutputMD summary are complete.
