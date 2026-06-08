# Gate Evidence Coverage Design

## Support Source

Gate support is derived from:

1. `gate.branchId`.
2. The matching worldline branch's `evidenceIds` and `temporalFactIds`.
3. Graph entities whose `evidenceId` matches those EvidenceAnchor ids.

If a gate does not have a branch, the selected event can be used as a fallback, but branch support is preferred because it is the narrower worldline decision context.

## UI Contract

- Gate cards keep their existing status/value/threshold/input layout.
- A new support row displays compact `Evidence / Graph / Time` counts.
- Focus Dossier keeps the existing normalized chip model and reuses Evidence Rail focus behavior implemented in the previous stage.

## Risk Control

The change is read-only frontend derivation. Missing support remains visible as `0` rather than fabricating targets.
