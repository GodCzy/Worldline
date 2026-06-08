# Agent Run Diff Timeline

Date: 2026-06-05

## Goal

Make the Agent workbench run ledger feel replayable over time by adding a compact scrub lane for run events and their structural deltas.

## In Scope

- Add a replay lane to the existing Run Events panel.
- Convert each event summary into visible diff chips for branches, episodes, tools, gates, artifacts, skills, permissions, evidence, and timeline facts.
- Selecting a replay step synchronizes the selected Event Detail.
- Preserve existing Run Manifest, Branch Dossier, Episode Dossier, and Skill Dossier behavior.
- Validate build and browser interaction.

## Out of Scope

- No backend schema change.
- No new visualization dependency.
- No unrelated worktree cleanup.
