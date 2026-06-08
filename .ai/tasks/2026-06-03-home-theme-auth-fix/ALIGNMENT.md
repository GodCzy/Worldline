# Home, Theme, Auth Fix Alignment

Updated: 2026-06-03

## Goals

- Make the home page, theme hub, Worldline hub, workbench, login panel, and sidebar share one premium dark visual language.
- Keep the palette consistent: near-black surfaces, restrained cyan energy, warm gold emphasis, and low-noise borders.
- Keep `/themes` empty for now except for a single custom-module `+` entry.
- Keep login embedded in the home page. Unauthenticated `Agent` access should return to `/?login=1&redirect=/agent`.
- Create and verify the local `Joy` superadmin account without storing the plaintext password in files.
- Preserve current backend API, router, and Worldline service contracts.

## Boundaries

- Do not restore old demo modules, old preview adapters, or old public-stage copy.
- Do not write tokens, plaintext passwords, API keys, or private account material into Markdown, screenshots, commits, or logs.
- Do not change database schema in this cleanup; use controlled account bootstrap only.
- Do not implement the real custom-module creation flow yet. The `+` entry is a placeholder entry point.

## Acceptance

- The first viewport uses the same dark cyan/gold Worldline identity as the workbench.
- `/themes` shows only the custom add entry, with no legacy demo card.
- `/worldline` shows a clean empty state when no module is available.
- Unauthenticated `/agent` redirects to the embedded home login panel.
- Authenticated Joy superadmin state exposes the expanded admin sidebar.
- Frontend build and Playwright screenshots pass on desktop and mobile viewports.
