# Evidence

Date: 2026-06-15

## Backend

- `py_compile` for P5 service, release gate, public demo router, auth/router wiring, and focused tests: passed.
- `ruff check` for P5 service, release gate, public demo router, auth/router wiring, focused tests, and Edge QA script: passed.
- `pytest test/test_worldline_public_demo_service.py test/test_worldline_phase6_7_release_gate.py -s`: `9 passed, 1 warning`.

## Frontend

- `web` Vite production build: passed. Existing vendor chunk-size warnings remain.
- Edge static QA: passed.
  - desktop `1440x900`: `screenshots/p5-public-demo-desktop.png`
  - mobile `390x844`: `screenshots/p5-public-demo-mobile.png`
  - report: `p5-public-demo-qa-report.json`

## Release And Docs

- `scripts/worldline_phase6_7_release_gate.py --codex-skills-root /mnt/c/Users/Joy/.codex/skills --output .ai/tasks/2026-06-15-p5-public-demo-share-export/release-gate-report.json`: passed, `12/12` checks.
- `vitepress build docs`: passed.
- `docker compose config`: passed.
- `git diff --check`: passed with CRLF normalization warnings for touched Windows-side files.

## Notes

- Running release gate without `--codex-skills-root /mnt/c/Users/Joy/.codex/skills` fails in WSL because the default `/home/joy/.codex/skills` path does not contain the Windows-installed local Worldline skills.
- GitHub PR/issue integration and optional ingestion tools remain external authorization rows by design; no remote connector was enabled.
