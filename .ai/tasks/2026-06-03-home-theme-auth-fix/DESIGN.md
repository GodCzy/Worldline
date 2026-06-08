# Home, Theme, Auth Fix Design

Updated: 2026-06-03

## Frontend

- Use one shared Worldline identity across pages: black base, cyan primary glow, gold highlights, subtle glass surfaces, and compact workbench typography.
- Home becomes the command console: left-side system status and worldline visual, right-side embedded login/init panel.
- Theme hub becomes a module registry placeholder: one `+` card only, no default business module.
- Worldline hub keeps the question input and workbench entry structure, but shows a clean empty module state.
- The sidebar uses the same dark shell and adds admin-only items when the current user is superadmin.
- The unauthenticated Agent route goes through router guard to the embedded home login panel.

## Backend And Account

- `scripts/ensure_superadmin.py` provides a future controlled account bootstrap path.
- The actual local Joy account was verified as `superadmin` in Postgres.
- Password material stays outside files and final reports.

## Risks

- Local Python dependency sync is currently blocked by package download TLS failure, so backend pytest did not run in this pass.
- Screenshot QA uses mocked authenticated state for the sidebar, while the database account was verified separately.
