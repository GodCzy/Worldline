# Design

## Current Behavior

Run Event detail sections already render clickable tokens. `focusEventDetailToken` selects the local target and opens a focus dossier, but it does not call the backend run resource inspector.

## Proposed Behavior

Add a mapper from event token target to the existing `inspectBackendManifestResource` resource shape:

- `artifact` -> `worldline.inspect_run_artifacts`
- `gate` -> `worldline.inspect_run_gates`
- `evidence` and `source` -> `worldline.inspect_run_evidence`
- `wiki`, `graph`, `timeline` -> `worldline.inspect_run_knowledge`

After local focus succeeds, call the inspector if the token is backend-inspectable and the active backend run is available.

## UX

No new major layout. The existing Resource Detail panel in the backend manifest area becomes the authoritative drilldown view.

## Validation

Chrome CDP QA will:

- Load a backend run with an event containing `artifactIds`.
- Click the artifact token in Event Detail.
- Assert `GET /api/worldline/runs/{run_id}/artifacts/read?artifact_id=...` is requested.
- Assert Resource Detail loads and the focus dossier targets the artifact.
