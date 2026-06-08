# Design

## Registry Sources

- Planned replay export: `replayArtifactRegistryPayload(replayExportArtifact)`.
- Planned handoff capsule: `handoffArtifactRegistryPayload(agentHandoffCapsule)`.
- Saved artifacts: `savedReplayArtifacts`.

Saved artifacts replace matching planned artifacts by `id`. Planned items are labeled `planned`; saved items are labeled `saved`.

## Filters

- `all`: all registry artifacts.
- `replay`: `kind/type` is `replay_export`.
- `handoff`: `kind/type` is `agent_handoff_capsule`.
- `other`: anything else.

## Safety

- The registry is display/focus only.
- Writes still require explicit `Save Artifact` or `Save Handoff` through existing admin-gated operations.
