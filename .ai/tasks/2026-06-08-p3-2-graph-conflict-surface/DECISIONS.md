# Decisions

## D1. Add a review panel before replacing GraphCanvas

Reason: the current GraphCanvas is shared with legacy graph browsing. A compact review panel lets the Temporal Knowledge Graph contract become visible without destabilizing the existing canvas.

## D2. Use Worldline APIs directly

Reason: P3-2 assets live in `/api/knowledge/databases/{db_id}/graph/*` and `/timeline`, not only the legacy `/api/graph/subgraph` endpoint.

## D3. Keep rebuild explicit

Reason: rebuilding graph state is a write-like backend action. The UI exposes it as a button instead of silently rebuilding on page load.

## D4. Keep this slice as a compact review panel

Reason: the backend conflict contract is now visible and reviewable, while deeper graph/timeline focus navigation can remain a later P3-2 slice. This avoids a broad `GraphCanvas` rewrite before the conflict evidence path is stable.
