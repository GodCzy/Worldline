# Design

## Method

- Enumerate matching task directories from `.ai/tasks`.
- Read `EVIDENCE.md`, `TASKS.md`, and top-level helper files.
- Use evidence wording to classify:
  - backend pytest passed
  - backend smoke/OpenAPI only
  - frontend build/browser QA only
  - mocked/CDP frontend QA
  - historical local preview/superseded
- Separately scan for `chrome-profile*`, `Cache`, `Code Cache`, `GPUCache`, and `chrome-cdp*.log`.

## Boundaries

- This audit does not delete files. P2-3 owns cleanup.
- This audit does not promote any mock result to backend-complete status.
