# Decisions

## D1. Public Means Read-Only

Public demo endpoints expose only deterministic, curated demo data. They do not grant access to live KBs, run ledgers, admin actions, or connector operations.

## D2. External Integrations Stay Gated

GitHub and optional ingestion tools remain external rows because they require account authorization, source review, and secret handling. P5 can be locally complete only by proving the gate and rollback boundary.

## D3. Bundle Export Is A Capsule

The export contains the selected branch, evidence refs, wiki refs, graph refs, temporal refs, quality gates, replay steps, rollback notes, and a stable checksum.
