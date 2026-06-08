# Agent Episode Replay

Date: 2026-06-05

## Goal

Make the Worldline Agent workbench use the backend-preserved `AgentEpisode` fields that are currently underrepresented in the frontend: `diffs`, `screenshots`, and `artifactIds`.

## User Concerns Covered

- Frontend still misses some backend capability.
- Knowledge graph and evidence work should stay inspectable through the worldline flow.
- The Agent workbench should feel like a replayable worldline console, not a static dashboard.

## In Scope

- Enrich local AgentEpisode preview data with replay metadata.
- Make episode cards focusable and keyboard accessible.
- Add an Episode Replay dossier that links tools, gates, artifacts, diffs, and screenshots.
- Validate `/worldline/agent` build and browser state.

## Out of Scope

- No backend schema change.
- No destructive git cleanup.
- No new dependencies.
