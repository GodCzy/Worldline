# Agent Replay Export

Date: 2026-06-05

## Goal

Turn the current Agent workbench replay state into a reviewable local artifact that can be downloaded, copied, or previewed.

## In Scope

- Generate a structured JSON replay artifact from the current run, selected event, replay lane, and focused Dossier.
- Generate a Markdown summary for human review.
- Add local export controls to the Run Ledger rail.
- Validate build and browser interaction.

## Out of Scope

- No backend persistence change.
- No schema migration.
- No external storage or third-party export service.
- No unrelated worktree cleanup.
