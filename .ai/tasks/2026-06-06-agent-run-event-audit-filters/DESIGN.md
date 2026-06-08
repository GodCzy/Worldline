# Design

## UI

Add a compact audit toolbar below the existing event-kind chips:

- Search input.
- Actor select.
- Export JSON button.
- Reset button.
- Status line showing filtered count over loaded count.

## Data Model

Use existing loaded `visibleLedgerEvents` as the source. `filteredLedgerEvents` becomes:

1. Apply event-kind chip.
2. Apply search query.
3. Apply actor filter.

## Export

Create a local JSON download with:

- `schema`: `worldline.run_event_audit.v0.1`
- `runId`
- `exportedAt`
- `filters`
- `counts`
- `events`

The export is a browser download only, avoiding backend and artifact registry contract churn.

## Validation

- Chrome CDP mocks a loaded backend run with mixed actors and event types.
- QA applies search and actor filters, verifies filtered rows, triggers export, and checks the export message.
