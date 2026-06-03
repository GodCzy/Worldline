# Decisions

## D1 - Keep SVG First

Phase 5 keeps the main worldline visual in SVG. Three.js is deferred because the current goal is a reliable operational workbench with screenshot QA, not immersive 3D.

## D2 - Add `phase5-preview`

The project needs deterministic frontend screenshot coverage even when no live backend or admin session is available. `phase5-preview` is a current validation adapter, not old demo content and not a persisted knowledge source.

## D3 - Optional Payload Fields Only

Backend and store changes are additive. Existing worldline payloads remain hydratable.

## D4 - Graph Page Stays Admin Surface

`/graph` keeps its admin guard. Screenshot automation may mock auth/API responses, but product routing still respects the existing permission contract.
