# Design

## Existing Contract

`GET /api/worldline/runs` already accepts:

- `limit`
- `offset`
- `query`
- `status`
- `theme_id`
- `created_by`

The service returns `items`, `total`, `limit`, `offset`, `filters`, and read-only storage metadata.

## Frontend

Add:

- `LEDGER_RUN_PAGE_SIZE = 8`
- `canLoadMoreLedgerRuns`
- `refreshLedgerRuns({ append = false })`
- `loadMoreLedgerRuns()`

Refresh uses offset `0` and replaces the list.

Load More uses offset `ledgerRunList.length` and appends returned rows, de-duplicated by id. The selector displays all loaded rows rather than slicing to the first eight.

## Validation

- `git diff --check`.
- `npm --prefix web run build`.
- Chrome CDP QA with mocked paginated backend responses.
