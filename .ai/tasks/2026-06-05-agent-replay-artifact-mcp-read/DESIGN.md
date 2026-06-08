# Design

## Tool

`worldline.inspect_run_artifacts`

Input:

- `run_id` required
- `artifact_id` optional
- `include_content` default `false`
- `limit` default `20`

Output:

- `run_id`
- `total`
- `items`
- optional `selected`
- `content_included`
- `storage`

## Security

- Read-only tool: `write_scope: none`.
- No filesystem path is exposed beyond the logical `worldline-run-ledger://...` URI already used by artifact registry.
- The implementation calls the service boundary, not raw database or arbitrary file APIs.
- An audit summary is recorded with `tool_name = worldline.inspect_run_artifacts`.

## Compatibility

- No change to existing write tools.
- Existing `all_write_tools_require_admin` checks remain valid because the new tool is read-only.
- Missing run returns an empty, explicit result instead of throwing an unstructured file error.
