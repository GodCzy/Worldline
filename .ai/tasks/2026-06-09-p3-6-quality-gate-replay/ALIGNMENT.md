# P3-6 Quality Gate Replay Alignment

## Goal

Complete P3-6 so a failed Quality Gate run is explainable and replayable from the Worldline UI.

## Scope

- Add backend replay references to failed `QualityGateRun.failure_replay` entries.
- Preserve the existing quality gate API response shape and add optional compatible fields only.
- Surface the latest failed gate in the branch inspector without turning the page into a dense configuration screen.
- Let failure refs jump to Evidence, Wiki, Graph, Timeline, and Run context.
- Prove the flow with an intentional failure test and frontend/browser verification.

## Out Of Scope

- No schema migration unless existing JSON storage is insufficient.
- No replacement of the current Worldline workbench layout.
- No unrelated graph, wiki, or MCP refactor.
- No remote deployment.

## Acceptance

- Backend stores failure reasons and refs for evidence, wiki, graph, timeline, and run.
- An intentional failed gate produces `failure_replay` with jump targets.
- Branch inspector renders a compact replay panel for a failed latest gate.
- Replay controls can navigate or focus the related evidence chain.
- Focused pytest and frontend build pass, or any failure is recorded with the exact blocker.
