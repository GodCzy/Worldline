# Design

## Interaction

The replay lane sits between event filters and the event list. It renders the current ledger events in replay order and uses the same `selectedLedgerEvent` state as Event Detail.

## Data

Each replay step derives deltas from `event.summary`:

- `branch_ids` / `branch_count`
- `episodeIds` / `episode_count`
- `skillProposalIds` / `skill_proposal_count`
- `evidenceIds`, `toolCallIds`, `temporalFactIds`, `gateResultIds`, `artifactIds`, `requiredPermissions`

## Visual Rules

- Keep the lane dense and scan-friendly.
- Use buttons for scrub steps so keyboard/mouse behavior stays predictable.
- Use existing cyan/gold chip language.
