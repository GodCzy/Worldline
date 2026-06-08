# Alignment

## Goal

Upgrade Worldline toward an Agent Workbench where each agent task is represented as an inspectable worldline run with branches, evidence, tool traces, quality gates, and skill proposals.

## Stage 1 Scope

- Add a first usable `/worldline/agent` workbench entry.
- Keep the current `/worldline` hub and theme-specific workbench compatible.
- Provide local deterministic preview data when backend run-ledger APIs are not available.
- Surface the future public contract for `WorldlineRun`, `WorldlineBranch`, `AgentEpisode`, and `SkillProposal`.
- Avoid database schema changes in this pass.

## Out Of Scope

- Persistent run ledger tables and migrations.
- Real multi-agent execution.
- Direct filesystem, database, or remote GitHub writes.
- Replacing existing Worldline knowledge, graph, wiki, or quality-gate contracts.

## Acceptance Criteria

- `/worldline/agent` renders without login and without backend availability.
- The page shows a task worldline canvas, selected branch inspector, evidence/tool trace panels, quality gates, and skill proposals.
- The page can be reached from the Worldline hub.
- Frontend build passes.
