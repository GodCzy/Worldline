# Agent Run Replay Manifest

Date: 2026-06-05

## Goal

Expose the backend run event summary fields as a replayable Worldline manifest in the Agent workbench.

## Backend Capability Being Surfaced

`WorldlineRunLedgerService._run_event_summary` already provides:

- `branch_ids`
- `episode_count`
- `skill_proposal_count`
- existing evidence/tool/timeline/gate/artifact summary fields

The frontend currently emphasizes evidence/tool/gate/artifact chips, but does not present the whole run as a replay manifest.

## In Scope

- Add run manifest metadata to local preview events.
- Add Branch, Episode, and Skill token sections in Event Detail.
- Add Branch Dossier.
- Add Run Replay Manifest Dossier with links to branches, episodes, gates, artifacts, and skills.
- Validate build and browser behavior.

## Out of Scope

- No backend schema change.
- No new dependencies.
- No cleanup of unrelated dirty worktree files.
