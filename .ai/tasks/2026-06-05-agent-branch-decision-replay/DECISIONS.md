# Decisions

## Use Existing Ledger Contract

Decision: do not add a new API or payload shape. Frontend reject uses the existing `worldlineRunApi.rejectBranch` wrapper.

Reasoning: backend service, router, and tests already prove the reject branch contract. The product gap is frontend reachability and user-visible replay.

## Gated In Local Preview

Decision: keep reject behind the same `canUseRunLedger` access gate as approve.

Reasoning: branch rejection is a write operation. In local preview or non-admin state, the UI must report that backend writes are unavailable rather than mutating local state as if the ledger accepted it.
