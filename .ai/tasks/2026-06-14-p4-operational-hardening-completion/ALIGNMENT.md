# P4 Operational Hardening Completion Alignment

Date: 2026-06-14

## Goal

Complete all P4 items in `docs/product/worldline-completion-matrix.md`.

## Acceptance

- Controlled requeue execution exists behind admin/service boundaries and writes audit evidence.
- Source version changes can mark sources/wiki pages stale and enqueue rebuild workflows.
- KB/run/branch/gate budgets are configurable and visible in the operational health report.
- Dashboard has a compact P4 operational panel with advanced controls in a drawer.
- Cleanup routines cover temporary files, deleted-KB readiness, MinIO objects, and archived artifacts without unsafe broad deletion.
- Focused backend tests, frontend build/static checks, docs build, Docker compose config, and screenshot QA are recorded.

## Boundaries

- Do not add schema churn unless unavoidable.
- Do not perform uncontrolled MinIO or filesystem deletion.
- Keep external writes behind Worldline services and admin endpoints.
- Preserve existing `/api/dashboard/worldline/operational-health` read contract.
