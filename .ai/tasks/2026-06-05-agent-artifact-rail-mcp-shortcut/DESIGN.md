# Design

## UI

Artifact Rail item rendering changes from one full-row button to:

- main artifact button for focus.
- secondary `Copy MCP` button for read-only MCP call.
- local status message inside Artifact Rail after copy/fallback.

## Reuse

The shortcut uses the existing Registry MCP helper:

- `registryArtifactRunId`
- `registryArtifactUri`
- `registryArtifactMcpArgs`
- `copyRegistryArtifactMcpCall`

## Safety

- The shortcut is read-only.
- It keeps `include_content: false`.
- It only copies instructions or shows a clipboard fallback status in the same rail where the action was clicked.
