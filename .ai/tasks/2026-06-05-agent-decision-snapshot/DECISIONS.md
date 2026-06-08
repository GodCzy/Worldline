# Decisions

## Frontend-Only Replay Improvement

Decision: implement Decision Snapshot entirely in the Agent Workbench view using existing event summary fields.

Reasoning: the backend already emits the needed decision data. The missing product behavior is frontend replay visibility, not a new API contract.

## No Synthetic Success Event

Decision: browser QA will validate layout with existing preview/fixture data and local interaction, not fabricate a backend write success in unauthenticated state.

Reasoning: branch decisions are ledger writes and must remain admin-gated.
