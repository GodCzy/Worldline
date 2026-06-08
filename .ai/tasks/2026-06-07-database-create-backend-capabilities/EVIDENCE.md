# Evidence

## Planned Checks

- `git diff --check -- web/src/views/DataBaseView.vue .ai/tasks/2026-06-07-database-create-backend-capabilities`
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && /home/joy/.local/bin/npm --prefix web run build"`
- in-app Browser smoke on `http://127.0.0.1:5173/database`

## Results

- `git diff --check -- web/src/views/DataBaseView.vue .ai/tasks/2026-06-07-database-create-backend-capabilities`
  - Result: passed.
  - Note: Git reported the existing CRLF normalization warning for `web/src/views/DataBaseView.vue`.
- Frontend build:
  - Command: `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && /home/joy/.local/bin/npm --prefix web run build"`
  - Result: passed in 3m26s.
  - Residual warning: existing Vite large chunk warning for vendor bundles such as `vendor-g6` and `vendor-antdv`.
- CDP frontend QA:
  - Command: `C:\Users\Joy\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe .ai\tasks\2026-06-07-database-create-backend-capabilities\qa-database-create-backend-capabilities-cdp.mjs`
  - Result: passed.
  - Mocked admin auth and backend endpoints:
    - `/api/auth/me`
    - `/api/system/info`
    - `/api/knowledge/types`
    - `/api/knowledge/databases`
    - `/api/knowledge/embedding-models/status`
  - Covered:
    - Database page renders under admin auth.
    - Create modal shows compact required fields.
    - `高级后端配置` opens on demand.
    - Private switch maps to `additional_params.is_private`.
    - Chunk parser override maps to `additional_params.chunk_parser_config`.
    - Backend payload preview masks sensitive token path and shows submitted structure.
  - Screenshot: `screenshots/database-create-backend-capabilities.png`.
