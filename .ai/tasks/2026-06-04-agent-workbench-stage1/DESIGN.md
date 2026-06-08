# Design

## Product Shape

The new view is an Agent Workbench preview, not a chat page. The page treats an agent task as a worldline run:

- The root is the user's goal.
- Branches represent planner, evidence, tool action, review, rejection, and skill-evolution paths.
- Each branch keeps visible proof: evidence refs, tool calls, temporal notes, quality gates, and next actions.

## Data Strategy

Stage 1 uses a local deterministic payload shaped like the future backend contract:

- `WorldlineRun`
- `WorldlineBranch`
- `AgentEpisode`
- `SkillProposal`

The payload is intentionally compatible with the existing `worldlineStore.hydrate` shape so existing Worldline canvas components can be reused.

## UI Strategy

- Left rail: run ledger and branch filters.
- Center: reused Worldline branch canvas and timeline scrubber.
- Right rail: inspector, evidence refs, tool trace, quality gates, skill proposals.
- Bottom input: local task prompt and branch regeneration.

## Contract Boundary

The frontend may add API wrappers for future run-ledger endpoints, but this pass does not require backend persistence. All future write actions must still go through Worldline service/MCP audit boundaries.
