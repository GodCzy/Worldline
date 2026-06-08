# Design

## Data Flow

1. The workbench builds `agentHandoffCapsule`.
2. `handoffArtifactRegistryPayload` wraps the capsule as a run ledger artifact.
3. `saveAgentHandoffCapsule` uses `ensureLedgerRun` and `worldlineRunApi.registerRunArtifact`.
4. The returned artifact list updates the existing registry rail.

## Artifact Shape

- `id`: `agent-handoff-<event_id>`
- `kind`: `agent_handoff_capsule`
- `format`: `json+markdown`
- `content`: full handoff capsule
- `markdown`: readable capsule summary

## Safety

- The UI action is disabled without admin access.
- It uses the same `runLedgerOperation` gate as other ledger writes.
- The handoff capsule itself remains read-only: `write_scope: none`.
