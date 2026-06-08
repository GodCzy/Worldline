# Design

## Current Behavior

The workbench loads paginated run events through `listRunEvents`. Some mutations also return `latestEvent`, and `mergeLedgerResult` appends that event locally. This is useful as an optimistic local update, but it does not guarantee backend ordering, updated total count, or consistency after the loaded event window spans more than one page.

## Proposed Behavior

- Keep `mergeLedgerResult` compatible with mutation responses.
- Add a small post-mutation helper that refreshes the loaded event window only when the mutated run is the active backend run.
- Use `refreshLoadedLedgerEvents()` so the refresh limit is `max(LEDGER_EVENT_PAGE_SIZE, ledgerEvents.length)`.
- For mutations that target inactive selector rows, refresh the run list only and avoid touching the active event rail.

## Mutation Targets

- Active run rename.
- Active run archive/restore.
- Replay artifact registration.
- Handoff artifact registration.
- Branch approval/rejection.
- Skill proposal.

## Validation

- Chrome CDP QA mocks:
  - load active run and first event page.
  - rename active run.
  - backend returns `latestEvent`.
  - frontend refreshes `/events?limit=6&offset=0`.
  - event rail shows updated total and new mutation event.
- `git diff --check`.
- `npm --prefix web run build`.
