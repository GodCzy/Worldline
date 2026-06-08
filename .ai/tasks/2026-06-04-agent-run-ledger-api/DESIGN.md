# Design

## Storage

Stage 2 stores run-ledger data in `config.save_dir/worldline/runs.json`. This avoids schema churn while proving the API and workflow shape.

## API

- `POST /api/worldline/runs`
- `GET /api/worldline/runs/{run_id}`
- `GET /api/worldline/runs/{run_id}/events`
- `POST /api/worldline/runs/{run_id}/branches/{branch_id}/approve`
- `POST /api/worldline/runs/{run_id}/branches/{branch_id}/reject`
- `POST /api/worldline/runs/{run_id}/skills/propose`

All routes require admin access.

## Compatibility

The service accepts the Stage 1 frontend payload shape and normalizes it into `WorldlineRun`, `WorldlineBranch`, `AgentEpisode`, and `SkillProposal` fields.
