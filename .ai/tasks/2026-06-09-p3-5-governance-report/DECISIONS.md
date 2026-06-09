# P3-5 Governance Report Decisions

## Keep Governance Local

No external connector is enabled for this slice. The policy lists connector boundaries but does not authorize or install remote access.

## Static Release Gate

The release gate uses source-fragment checks for the governance report structures. This keeps the gate deterministic in local and CI-like environments where Codex connector state is unavailable.

## Compatible Report Shape

The existing governance report keys remain unchanged. New evidence is additive so existing callers that read `status`, `policy`, `servers`, `violations`, or `warnings` continue to work.
