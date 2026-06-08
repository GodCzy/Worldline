# Design

## UI

The `MCP READABLE` block lives inside the existing `REPLAY EXPORT` panel:

- status chip
- tool name: `worldline.inspect_run_artifacts`
- logical URI: `worldline-run-ledger://<run_id>/artifacts/<artifact_id>`
- JSON args preview
- copy button

## States

- `Registered`: at least one saved replay artifact exists.
- `Save required`: local preview or unsaved export; users can still see the planned tool call.

## Safety

- This is only a visible affordance for the already implemented read-only MCP tool.
- It does not enable writes or bypass admin-only save behavior.
- Clipboard failure falls back to a visible status message.
