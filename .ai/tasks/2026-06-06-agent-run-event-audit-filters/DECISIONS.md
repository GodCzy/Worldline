# Decisions

## 2026-06-06

- Keep audit filtering client-side for currently loaded events; server-side event query filters can be added later if event volume requires it.
- Export filtered event audit JSON as a browser download instead of registering it as a backend artifact in this step.
- Preserve existing event kind chips and pagination behavior.
