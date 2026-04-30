# Phase 56 - Playwright MCP `Transport closed` remediation

## Baseline

- Prior stable repo head: `5c81151 feat(worldline): unify shell flow and login redirect handoff`
- Reported blocker: MCP Playwright calls in current Codex session fail with `Transport closed`.
- User decision (2026-04-01): real-backend login interactive signoff can be deferred; first restore Playwright MCP availability.

## External evidence scanned (GitHub / forum / community)

1. `microsoft/playwright-mcp` README and CLI help show `--isolated` as first-class option to avoid persisted profile contention.
2. `openai/codex` issue #6649 includes a reproducible `Transport closed` case and user-side workaround direction around MCP Playwright startup/profile behavior.
3. `openai/codex` issue #4180 reports Windows failures caused by missing inherited environment variables (`SYSTEMROOT`, etc.), leading to MCP server startup issues.
4. `microsoft/playwright-mcp` issue #1113 highlights startup/connection instability patterns and checks around environment/version/state.
5. Cursor forum thread (`playwright-mcp-no-tools-enabled`) confirms Windows command wiring pitfalls (`npx`/args split and process startup style) as a practical failure source.

## Implemented local fix (outside repo, on this machine)

Updated local Codex config:

- File: `C:\Users\godcz\.codex\config.toml`
- Section: `[mcp_servers.playwright]`
- Changes:
  - switch command to explicit Windows executable:
    - `command = 'C:\Program Files\nodejs\npx.cmd'`
  - switch to package launch + isolation:
    - `args = ["-y", "@playwright/mcp@latest", "--isolated", "--headless", "--browser", "chromium"]`
  - increase startup/tool timeout:
    - `startup_timeout_sec = 90`
    - `tool_timeout_sec = 240`
  - add explicit Windows env keys for process bootstrap:
    - `SYSTEMROOT`, `COMSPEC`, `APPDATA`, `LOCALAPPDATA`, `USERPROFILE`, `PROGRAMDATA`

## Validation run

1. Package startup check:
   - `npx @playwright/mcp@latest --version` => `0.0.70`
2. Runtime bootstrap check:
   - start MCP with `--port 8945` and verify local listen socket => success (`MCP_PORT_LISTENING`)
3. In-session MCP tool probe:
   - previous fatal `Transport closed` no longer appeared
   - current blocker surfaced as filesystem permission:
     - `EPERM: operation not permitted, mkdir 'C:\Windows\System32\.playwright-mcp'`
   - interpretation:
     - transport layer progressed, but current Codex session still uses an unwritable default output path

## Follow-up local fix

Further update applied to local `C:\Users\godcz\.codex\config.toml`:

- add writable MCP output path to args:
  - `--output-dir C:/Users/godcz/.codex/playwright-mcp-output`
- pre-created target directory:
  - `C:\Users\godcz\.codex\playwright-mcp-output`

Expected effect:

- after restarting Codex session (or forcing MCP server reload), Playwright MCP should stop writing under `C:\Windows\System32` and use the user-writable output dir instead.

## Repository code changes in this pass

- No application source code changed.
- This pass focused on MCP runtime/tooling recovery and phase decision support.

## Phase judgment

- Current phase: `Phase 3 hardening / tooling reliability gate`
- Readiness for next phase:
  - `conditional-ready` if team accepts deferred real-backend login interactive signoff as known debt
  - `fully-ready` only after that signoff evidence is captured in a later acceptance pass
- Main remaining gap before advancing:
  - one deferred acceptance debt: real-backend login session handoff (`/worldline -> /login -> /agent`) evidence replay in a stable session
  - plus one tooling reload requirement: current session must reload MCP server config to pick up the new `--output-dir` args
