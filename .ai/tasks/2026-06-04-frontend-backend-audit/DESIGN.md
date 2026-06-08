# Design Notes

## Approach

1. Read current project facts from the active root.
2. Inventory frontend routes, stores, API calls, and workbench components.
3. Inventory backend routers and protected knowledge/worldline endpoints.
4. Compare frontend calls with backend route coverage.
5. Apply focused UI and integration fixes only where behavior is confirmed.
6. Validate with build, targeted tests where available, and screenshot or smoke checks.

## Integration Rules

- Preserve existing backend route shapes.
- Add optional frontend handling for backend fields instead of requiring server changes.
- Keep `worldlineStore.hydrate` compatible with `/worldline/generate` payloads.
- Surface evidence, wiki refs, entity refs, timeline refs, quality state, and workflow/MCP affordances where backend data is already available.

## Risk Areas

- Current worktree contains many uncommitted changes from earlier Worldline tasks.
- Some older task directories are intentionally deleted; they must not be restored as current facts.
- Backend tests may be limited by local dependency or service availability.
- The project files include prior Chinese text; PowerShell default output may display mojibake even when files are UTF-8.
