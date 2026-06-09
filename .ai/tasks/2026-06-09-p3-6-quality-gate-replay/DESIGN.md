# P3-6 Quality Gate Replay Design

## Backend

`WorldlineQualityGateService.run_gate` already computes metrics and failures, then persists a JSON `failure_replay` payload. P3-6 enriches that payload with:

- `reason`: deterministic explanation of the failed check.
- `severity`: stable UI hint.
- `refs`: grouped references for `evidence`, `wiki`, `graph`, `timeline`, and `run`.
- `jump_targets`: flat actions the frontend can render as compact buttons.

The service will gather reference candidates from existing repository list methods, then add the current `gate_id` as the run ref. This avoids migrations and keeps old clients compatible because existing fields remain unchanged.

## Frontend

`WorldlineBranchDetailPanel` receives the current quality object and renders a compact Quality Gate Replay section only when the latest gate has failures. Each failure shows a short reason and small buttons for refs.

`WorldlineWorkbenchView` handles emitted replay refs:

- `evidence`, `wiki`, `timeline`, and `graph` map into existing graph-focus routing.
- `run` updates the live status message with the selected gate context.
- A strict gate action uses intentionally impossible thresholds to demonstrate replay without exposing complex configuration.

## Risk

- If live KB data has no wiki, graph, or timeline objects, the backend can only emit refs that exist. Tests seed all required layers.
- Current Vue files contain mojibake display text. This task only adds English labels around the new replay panel to avoid broad text churn.
