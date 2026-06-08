# Design

## Backend

The run ledger remains file-backed. The ledger JSON gains an optional top-level `artifacts` map:

```json
{
  "runs": {},
  "events": {},
  "artifacts": {
    "run-id": []
  }
}
```

Each artifact contains metadata plus serialized replay content:

- `id`
- `runId`
- `eventId`
- `kind`
- `format`
- `label`
- `summary`
- `content`
- `markdown`
- `createdBy`
- `createdAt`
- `updatedAt`

Registering an artifact also appends an `artifact.registered` ledger event, so the replay lane can show the export as part of the run chronology.

## Frontend

The existing `REPLAY EXPORT` panel gets a `Save Artifact` action. It uses `ensureLedgerRun()` first, then calls `worldlineRunApi.registerRunArtifact`. When admin/backend access is not available, the button remains disabled and local JSON/Markdown export still works.

Saved artifacts are displayed as a compact list and merged into the Artifact Rail as regular artifact details.

## Compatibility

- Existing run payloads and event summaries remain valid.
- Optional artifact fields are additive.
- The feature works with local preview even when backend is unavailable.
