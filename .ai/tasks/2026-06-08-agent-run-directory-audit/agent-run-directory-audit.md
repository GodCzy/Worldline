# Agent Run Directory Audit

Date: 2026-06-08

## Summary

Audited 53 directories matching `.ai/tasks/2026-06-0[456]-agent*`.

Use this report before staging or cleanup. A directory appearing here means the task has evidence, not that its feature is necessarily backend-complete.

## Backend Pytest Or Contract Evidence

These directories include focused pytest results or explicit backend contract suites. They are the strongest implementation evidence.

| Directory | Evidence |
| --- | --- |
| `2026-06-04-agent-event-evidence-links` | `test/test_worldline_run_ledger_service.py`: `2 passed`; py_compile and browser QA also passed. |
| `2026-06-04-agent-run-ledger-api` | container pytest: `2 passed`; router/service/test added for run ledger API. |
| `2026-06-05-agent-evidence-mcp-read-contract` | backend pytest: `9 passed`; frontend build and browser QA passed. |
| `2026-06-05-agent-gate-mcp-read-contract` | backend pytest: `8 passed`; frontend build and browser QA passed. |
| `2026-06-05-agent-knowledge-mcp-read-contract` | backend pytest: `10 passed`; frontend build and browser QA passed. |
| `2026-06-05-agent-replay-artifact-mcp-read` | focused backend tests passed: 4 tests and release gate 3 tests. |
| `2026-06-05-agent-replay-artifact-registry` | `.venv` pytest fallback passed: `2 tests passed`; build/browser QA passed. |
| `2026-06-05-agent-run-manifest-api-inspector` | backend contract: `11 passed`; build/browser QA passed. |
| `2026-06-05-agent-run-mcp-manifest-rail` | backend contract: `11 passed`; build/browser QA passed. |
| `2026-06-05-agent-run-resource-drilldown` | focused router test passed, then `11 passed`; build/browser QA passed. |
| `2026-06-06-agent-cross-run-diff` | backend router test passed and full focused suite `11 passed`; browser QA passed. |
| `2026-06-06-agent-run-maintenance-audit` | backend router test passed and full focused suite `11 passed`; browser QA passed. |
| `2026-06-06-agent-run-restore-audit` | backend router test passed and full focused suite `11 passed`; browser QA passed. |
| `2026-06-06-agent-run-selector` | backend router test and full focused suite passed; browser QA passed. |
| `2026-06-06-agent-run-selector-filters` | backend router test and full focused suite passed; browser QA passed. |

## Backend Smoke Or Contract Sketch

These have backend route smoke, service smoke, OpenAPI checks, or py_compile, but not a clean focused pytest result in their own evidence.

| Directory | Evidence |
| --- | --- |
| `2026-06-04-agent-event-detail-inspector` | OpenAPI route exposure, health, unauthenticated 401, build/browser QA. |
| `2026-06-04-agent-event-token-drilldown` | OpenAPI route exposure, health, compose config, build/browser QA. |
| `2026-06-04-agent-focus-dossier` | OpenAPI route exposure, health, compose config, build/browser QA. |
| `2026-06-04-agent-ledger-dossier-contract` | py_compile and direct service smoke passed; broader pytest blocked by dependency/TLS issues. |
| `2026-06-04-agent-workbench-event-timeline` | OpenAPI route exposure plus build/browser QA; no backend pytest. |
| `2026-06-04-agent-workbench-ledger-sync` | OpenAPI route exposure plus build/browser QA; notes future backend persistence. |

## Frontend Build And Browser QA

These are real UI evidence with build/browser/CDP screenshots, but should not be treated as backend-complete by themselves.

| Directory | Evidence |
| --- | --- |
| `2026-06-04-agent-artifact-rail` | frontend build and browser screenshots; explicitly no backend pytest. |
| `2026-06-04-agent-evidence-graph-timeline-linkage` | build and CDP interaction QA passed. |
| `2026-06-04-agent-gate-artifact-linkage` | build and browser interaction QA passed. |
| `2026-06-04-agent-gate-run-panel` | build and browser screenshots; explicitly no backend pytest. |
| `2026-06-05-agent-artifact-rail-mcp-shortcut` | diff check, build, browser QA passed. |
| `2026-06-05-agent-artifact-type-filter` | diff check, build, browser QA passed. |
| `2026-06-05-agent-branch-decision-replay` | build and CDP QA passed; notes no fake backend rejection. |
| `2026-06-05-agent-decision-snapshot` | build and CDP QA passed. |
| `2026-06-05-agent-episode-replay` | diff check and browser QA passed. |
| `2026-06-05-agent-focus-dossier-mcp-shortcut` | build and browser QA passed. |
| `2026-06-05-agent-gate-evidence-coverage` | diff check, build, browser QA passed. |
| `2026-06-05-agent-handoff-artifact-save` | diff check, build, browser QA passed. |
| `2026-06-05-agent-handoff-capsule` | diff check, build, browser QA passed. |
| `2026-06-05-agent-last-mcp-call-preview` | build and browser QA passed. |
| `2026-06-05-agent-registry-mcp-shortcut` | diff check, build, browser QA passed. |
| `2026-06-05-agent-replay-export` | diff check, build, CDP browser QA passed. |
| `2026-06-05-agent-replay-mcp-read-badge` | diff check, build, browser QA passed. |
| `2026-06-05-agent-run-diff-timeline` | diff check and browser QA passed. |
| `2026-06-05-agent-run-replay-manifest` | diff check and browser QA passed. |
| `2026-06-05-agent-skill-genome-dossier` | diff check and browser QA passed. |
| `2026-06-05-agent-source-dossier` | build and CDP QA passed. |
| `2026-06-06-agent-resource-detail-artifact-replay` | build and browser/CDP QA passed. |
| `2026-06-06-agent-resource-detail-artifact-save` | reused existing artifact API; build/browser QA passed. |
| `2026-06-06-agent-resource-detail-diff-artifact-save` | frontend contract only; build/browser QA passed. |
| `2026-06-06-agent-resource-detail-snapshot-diff` | frontend-only read wrapper; build/browser QA passed. |
| `2026-06-06-agent-run-bulk-maintenance` | diff check, build, browser QA passed. |
| `2026-06-06-agent-run-selector-pagination` | diff check, build, browser QA passed. |

## Mocked Frontend Or CDP QA

These evidence files explicitly mention mocked run lists/details/events/artifacts. They are useful UI evidence, but must not be counted as live backend validation.

| Directory | Evidence |
| --- | --- |
| `2026-06-06-agent-run-event-audit-filters` | browser QA passed with mocked run list, run detail, event page, artifact list. |
| `2026-06-06-agent-run-event-mutation-refresh` | browser QA passed with mocked run list, run detail, run event pages, artifacts, active run rename. |
| `2026-06-06-agent-run-event-pagination` | browser QA passed with mocked backend run list, run detail, artifact list, run event pages. |
| `2026-06-06-agent-run-event-resource-drilldown` | browser QA passed with mocked run list, run detail, event page, artifact list, artifact read endpoint. |

## Historical Local Preview

| Directory | Evidence |
| --- | --- |
| `2026-06-04-agent-workbench-stage1` | Stage 1 local preview; `worldlineRunApi` wrappers pointed at future endpoints then. Later backend work supersedes it. |

## Cleanup Candidates For P2-3

Do not delete screenshots, `EVIDENCE.md`, `TASKS.md`, or useful QA scripts. P2-3 can remove these cache/profile/log artifacts after verifying paths stay inside `.ai/tasks`.

- `2026-06-05-agent-focus-dossier-mcp-shortcut\chrome-profile`
- `2026-06-05-agent-gate-mcp-read-contract\chrome-profile`
- `2026-06-05-agent-last-mcp-call-preview\chrome-profile`
- `2026-06-05-agent-last-mcp-call-preview\chrome-profile-global`
- `2026-06-05-agent-evidence-mcp-read-contract\chrome-cdp.err.log`
- `2026-06-05-agent-evidence-mcp-read-contract\chrome-cdp.out.log`
- `2026-06-05-agent-knowledge-mcp-read-contract\chrome-cdp.err.log`
- `2026-06-05-agent-knowledge-mcp-read-contract\chrome-cdp.out.log`

## Staging Guidance

- Commit backend-tested directories with the code/tests that implement the same contract.
- Commit frontend-only directories with their Vue/API wrapper changes and screenshots.
- Keep mocked QA directories separate from backend contract commits.
- Do not `git add .`; use explicit paths after P2-3 cleanup.
