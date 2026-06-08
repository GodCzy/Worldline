# Evidence

## Commands

- `Get-ChildItem -Path .ai\tasks -Directory | Where-Object { $_.Name -match '^2026-06-0[456]-agent' }`
- `Select-String` scans over `TASKS.md` and `EVIDENCE.md` for `pytest`, `passed`, `mock`, `screenshot`, `browser`, `backend`, `frontend`.
- Recursive scan for `chrome-profile`, `Cache`, `Code Cache`, `GPUCache`, and `chrome-cdp*.log`.

## Results

- Matching directories: 53.
- Backend pytest/contract evidence directories: 15.
- Backend smoke or OpenAPI-only evidence directories: 6.
- Frontend build/browser QA directories: 27.
- Mocked frontend/CDP QA directories: 4.
- Historical local preview/superseded directory: 1.
- Cleanup candidates found:
  - `2026-06-05-agent-focus-dossier-mcp-shortcut\chrome-profile`
  - `2026-06-05-agent-gate-mcp-read-contract\chrome-profile`
  - `2026-06-05-agent-last-mcp-call-preview\chrome-profile`
  - `2026-06-05-agent-last-mcp-call-preview\chrome-profile-global`
  - `2026-06-05-agent-evidence-mcp-read-contract\chrome-cdp.err.log`
  - `2026-06-05-agent-evidence-mcp-read-contract\chrome-cdp.out.log`
  - `2026-06-05-agent-knowledge-mcp-read-contract\chrome-cdp.err.log`
  - `2026-06-05-agent-knowledge-mcp-read-contract\chrome-cdp.out.log`

## Report

- `D:\dev\Worldline\.ai\tasks\2026-06-08-agent-run-directory-audit\agent-run-directory-audit.md`
