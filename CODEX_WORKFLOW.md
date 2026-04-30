# CODEX_WORKFLOW.md

## Purpose

This file defines operational workflow defaults for Codex in `D:\worldline`.
`AGENTS.md` stores stable policy; this file stores execution-time procedure.

## Bootstrap Procedure

At the start of every substantial task, execute this order:

1. Read `AGENTS.md`.
2. Read `CODEX_WORKFLOW.md`.
3. Read the newest relevant file under `docs/context-cache/`.
4. Only then run targeted repository scanning needed by the task.

Bootstrap belongs here and should not be duplicated in `AGENTS.md`.

## Context-Cache Operating Rules

- Treat `docs/context-cache/` as compressed project memory.
- Do not bulk-load cache files; read only the newest relevant baseline and any directly related closure/signoff files.
- When stable conclusions are produced, create or update one concise cache file in the same turn.
- Prefer milestone-level cache files over fragmented micro-notes.
- Cache updates should include:
  - scope decisions and boundaries
  - validation outcome summary
  - phase readiness judgment
- Keep historical evidence immutable; move it out of active reading paths instead of rewriting content.

## Validation and Release Gates

Run the minimum feasible gates for the current phase and touched surface.

### Common build checks

- Frontend build: `pnpm --dir web build`
- Docs build: `npm run docs:build`
- Python syntax check (when backend/python touched): `python -m compileall server src`

### Phase 7 naming gate

For active-surface cleanup, enforce a grep gate on active files only:

`git grep -n -I -E "Y[U]XI|y[u]xi" -- . ":(exclude)docs/archive/**" ":(exclude)docs/context-cache/**" ":(exclude)artifacts/**" ":(exclude)uv.lock" ":(exclude)node_modules/**" ":(exclude).git/**" ":(exclude).playwright-cli/**"`

Pass condition: no output.

### Runtime smoke baseline

When runtime is available, verify:

- `/api/system/info`
- `/api/system/health`
- `/themes`
- `/worldline`
- `/agent`
- `/graph`

Prefer Playwright-based smoke for browser routes when UI behavior matters.

### Runtime closure gate (Phase 7 naming-related changes)

If the current task touches compose/image naming or default database naming, run an explicit runtime closure pass:

- Recreate key services with current compose definitions:
  - `docker compose up -d --build api web worker`
- Verify running image names are fully aligned with Worldline naming:
  - `docker compose ps --format json`
  - pass condition: `api`/`worker` use `worldline-api:*` and `web` uses `worldline-web:*`
- Verify runtime database naming is aligned:
  - `docker compose exec -T api env | Select-String "POSTGRES_URL|POSTGRES_DB|DATABASE_URL|DB_NAME"`
  - `docker compose exec -T postgres psql -U postgres -d postgres -lqt`
  - pass condition: runtime connection points to `worldline_know` and database exists in PostgreSQL
- Verify production compose path:
  - `docker compose -f docker-compose.prod.yml --env-file .env.prod config`
  - if this cannot be executed because `.env.prod` is missing, it must be marked as an explicit phase-closing blocker.

## Git Execution Rules

- If files changed and a stable stopping point is reached, run feasible validation and create a non-interactive commit unless user explicitly says not to.
- Never create empty commits.
- Never amend, rebase, or rewrite history unless user explicitly requests it.
- Do not commit noise paths such as:
  - `artifacts/`
  - `.playwright-cli/`
  - `test-results/`
- Use concise commit messages, preferably `type(scope): summary`.

## MCP and Skill Activation Rules

Use the smallest high-value set that removes current recurring friction.

### Priority judgment matrix

- Long-context planning, cross-phase handoff, token pressure:
  - Prefer `context-compression`.
  - Prefer `filesystem-context` for just-in-time file loading.
- Frontend page discovery, browser smoke, route-level behavior validation:
  - Prefer `playwright` skill + Playwright MCP.
- PR checks, CI failures, release coordination, review-thread handling:
  - Prefer GitHub MCP.
- Database connectivity checks, schema/data inspection, migration verification:
  - Prefer PostgreSQL MCP.
- External documentation/source extraction or citation-heavy dependency checks:
  - Prefer Fetch MCP.

### Phase-start MCP review

At the beginning of each substantial phase:

1. Judge whether current MCP coverage is sufficient.
2. Enable missing MCP only if it clearly reduces repeated manual work in that phase.
3. Record the MCP decision in context-cache when it affects workflow.

## Phase Baseline and Progression Rules

- Keep phase progression explicit and ordered.
- End each substantial task with:
  - current phase
  - readiness for next phase
  - main blocking gap if not ready
- Do not defer phase judgment until user asks.

## Response Contract Reminder

For substantial tasks, final response must include:

1. changed files
2. why changed
3. how to run/validate
4. remaining risks

Also include exactly one suggested next-turn prompt with:

- `先读：`
- `当前基线：`
- `本轮优先任务：`
- `主控最后汇总：`
- `要求：`
