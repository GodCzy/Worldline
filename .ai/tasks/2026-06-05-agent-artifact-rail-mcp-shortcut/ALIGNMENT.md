# Alignment

## Goal

Bring the item-level read-only MCP shortcut from the Replay Export Registry into the right-side Artifact Rail so artifact evidence can be copied from either workspace side.

## Scope

- Add a `Copy MCP` action to Artifact Rail items.
- Reuse the existing `worldline.inspect_run_artifacts` shortcut helper.
- Preserve artifact focus behavior and scope filters.

## Non-Goals

- No backend route or schema change.
- No new MCP tool.
- No automatic external Agent execution.
- No change to artifact source calculations.

## Acceptance

- Artifact Rail rows show `Copy MCP`.
- Clicking `Copy MCP` does not focus/switch artifact unintentionally.
- Copy status names the clicked artifact.
- Build and browser QA pass.
