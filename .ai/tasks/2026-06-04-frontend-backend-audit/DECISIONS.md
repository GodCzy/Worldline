# Decisions

- Use the active root `D:\dev\Worldline`, not the pointer folder.
- Treat pre-reset planning and deleted older task directories as historical only.
- Do not revert dirty files from prior work unless the user explicitly asks.
- Prefer frontend fixes that consume existing backend contracts before changing backend routes.
- Surface already-built backend capabilities through the Worldline workbench before adding new backend endpoints.
- Preserve live `db_id` / `knowledge_db_id` through route context so frontend navigation targets the intended knowledge database.
- Keep screenshot QA local and deterministic by mocking live backend responses in Playwright instead of requiring credentials or seed data.
- Store custom theme modules in `saves/config/theme_modules.json` via `/api/system/themes` instead of adding schema migrations; this keeps the feature backend-managed while avoiding unrelated database churn.
- Merge custom modules into the existing public `/api/system/info` response so `/themes`, `/worldline`, theme detail and layout consumers share one module source.
- For protected-page visual QA, create a short-lived local-only QA account only when needed, record the action, and delete it immediately after screenshots. Do not retain or reuse QA credentials.
