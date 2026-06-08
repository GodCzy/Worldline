# Design

## Existing Contract

`GET /api/worldline/runs/{run_id}/events` already accepts:

- `limit`
- `offset`

The response includes `items`, `total`, `limit`, and `offset`.

## Frontend

Add:

- `LEDGER_EVENT_PAGE_SIZE = 6`
- `ledgerEventsTotal`
- `ledgerEventsBusy`
- `canLoadMoreLedgerEvents`
- `refreshLedgerEvents({ append = false })`
- `refreshLoadedLedgerEvents()`
- `loadMoreLedgerEvents()`

The first refresh replaces the loaded events. Load More appends and deduplicates by event id. Any run mutation that affects events can refresh the currently loaded event window when needed.

## Validation

- `git diff --check`.
- `npm --prefix web run build`.
- Chrome CDP QA with mocked event pages.
