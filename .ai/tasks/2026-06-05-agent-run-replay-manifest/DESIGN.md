# Design

## Interaction

- Run events get an `Open Replay Manifest` action in Event Detail.
- Run Manifest Dossier reuses the existing Focus Dossier rail.
- Branch links focus the matching branch, select it on the canvas, and open a Branch Dossier.
- Episode and Skill links reuse the Dossiers added in previous stages.

## Data

The local preview run event now includes backend-compatible `branch_ids`, `episode_count`, and `skill_proposal_count`. It also includes optional local convenience arrays `episodeIds` and `skillProposalIds` so the preview can render clickable replay links before the backend adds those IDs to event summaries.

## Visual Rules

- Keep the right rail compact.
- Use existing token chips and Dossier metadata styles.
- Avoid adding a separate page or dashboard.
