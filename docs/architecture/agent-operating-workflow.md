# Agent Operating Workflow

更新时间：2026-06-08

## Purpose

This document defines how Codex, subagents, local Worldline skills, MCP tools, Browser/Playwright, and GitHub should be used to develop Worldline without losing evidence, bypassing service boundaries, or turning a dirty worktree into an unreviewable commit.

## Control Model

Worldline uses one main controller Agent per task.

The main Agent owns:

- Scope and acceptance criteria.
- Final file edits.
- Tool and MCP decisions.
- Worktree hygiene.
- Verification.
- Final summary and commit boundaries.

Subagents are optional sidecars. They do not replace the main controller.

## Subagent Lanes

Use subagents only when the task explicitly benefits from delegation or when the user asks for multi-agent work.

| Lane | Typical role | Write access | Output |
|---|---|---:|---|
| Research Review | Audit docs, compare options, inspect external references | No | Findings, risks, citations |
| Code Explorer | Read code and answer a bounded architecture or contract question | No | File/line findings |
| Knowledge Operation | Inspect knowledge pipeline, evidence, Wiki, graph, timeline, quality gates | Usually no; write only if explicitly assigned disjoint files | Contract report or bounded patch |
| Frontend QA | Run local Browser/Playwright screenshots and responsive checks | No, unless assigned a UI patch | Screenshot report and issues |
| Release Audit | Run validation commands, inspect staged diff, verify OutputMD | No | Pass/fail report |
| Worker | Implement a narrow patch in a disjoint file set | Yes, explicitly scoped | Changed paths and verification |

Rules:

- Do not assign the immediate blocking critical-path task to a subagent.
- Do not have multiple agents edit the same files.
- Subagents must not revert unknown changes.
- Subagents must state whether they modified files.
- Main Agent integrates and verifies all results.

## Local Codex Skills

Use the Worldline local skills as task gates:

| Skill | Use when | Required output |
|---|---|---|
| `worldline-orient` | Any Worldline planning, implementation, cleanup, or review | Confirm `D:\dev\Worldline`, facts, dirty worktree |
| `worldline-backend-contract` | FastAPI routers, services, repositories, storage models, MCP tools, tests | Preserve API/storage/service contracts and focused tests |
| `worldline-knowledge-pipeline` | SourceAsset, DocumentVersion, DocumentNode, EvidenceAnchor, WikiPage, graph, temporal facts, RAG, gates | Keep evidence-bound pipeline and quality gates |
| `worldline-frontend-workbench` | `/worldline`, `/graph`, themes, dashboard, UI QA | Preserve compact console UX and screenshot gates |
| `worldline-mcp-governance` | MCP manifests, tools, permissions, external Agent writes | Record permissions, disabled defaults, audit and rollback |
| `worldline-eval-release` | Final validation and task summary | Run relevant checks and write OutputMD |

## MCP And Tool Policy

Recommended by default:

- Internal `worldline` MCP boundary for application writes.
- Browser/Playwright for local UI smoke and screenshot QA.
- GitHub for PR, issue, and CI tasks when remote context is necessary.

Conditional:

- Firecrawl, Context7, Tavily, Figma, Notion, Linear.
- Enable only for a task with explicit need and a recorded review of source, license, command, args, env, network reach, write scope, data exposure, and rollback.

Not default:

- Database-write MCP.
- Unrestricted filesystem MCP.
- Shell/command MCP.
- Docker/Kubernetes admin MCP.
- Slack/Email/Calendar or other external communication write MCP.

Secrets never go into repo, Markdown, URLs, screenshots, task evidence, or Agent instruction files.

## Standard Task Workflow

### 1. Orient

Read:

- `AGENTS.md`
- `README.md`
- `docs/index.md`
- Active `.ai/tasks/<date-task>/`

Run:

```powershell
git status --short --branch
```

Record unrelated dirty work and do not overwrite it.

### 2. Align

Create `.ai/tasks/<YYYY-MM-DD-task>/ALIGNMENT.md` with:

- Goal
- Non-goals
- Acceptance evidence
- Risk boundaries
- Tooling expectations

### 3. Design

Create `DESIGN.md` with:

- Data objects
- API routes
- UI surfaces
- MCP/tool effects
- Tests and rollback

### 4. Atomize

Create `TASKS.md` with verifiable slices.

Prefer vertical product slices:

```text
Source -> Evidence -> Wiki/Graph/Timeline -> Quality Gate -> Worldline UI -> Agent Replay
```

### 5. Implement

Use existing stack and patterns first:

- FastAPI, ARQ, Redis, Postgres, MinIO, Milvus, Neo4j
- Vue 3, Vite, Pinia, Ant Design Vue
- LangGraph and controlled MCP
- Docling, LightRAG, LlamaIndex as already scoped

Do not introduce broad dependencies without a design note and rollback path.

### 6. Validate

Use checks proportionate to the changed surface:

```powershell
git diff --check
docker compose config
pnpm --dir web build
npm run docs:build
```

Backend contract changes should add focused pytest.

Frontend changes should add Browser/Playwright desktop and `390x844` screenshots when layout or interaction changes.

### 7. Record

Update:

- `.ai/tasks/<date-task>/EVIDENCE.md`
- `.ai/tasks/<date-task>/DECISIONS.md`
- `D:\document\OutputMD\YYYY-MM-DD-Worldline-<task>.md`

Record failures and residual risk honestly.

### 8. Clean And Commit

Before staging:

```powershell
git status --short --branch
git diff --name-status
git ls-files --others --exclude-standard
```

Never use `git add .` on a dirty Worldline worktree.

Stage one logical package at a time:

```powershell
git add -- <explicit paths>
git diff --cached --name-status
git diff --cached --check
```

Commit only after the package has coherent scope and validation evidence.

## Worktree Hygiene Rules

Always remove or ignore:

- Browser profiles and caches.
- CDP logs.
- Build output.
- `node_modules`.
- Python virtual environments.
- `.env` and local secret files.
- Temporary archives or installers.

Always preserve unless explicitly superseded:

- `.ai/tasks/<date-task>/ALIGNMENT.md`
- `DESIGN.md`
- `TASKS.md`
- `EVIDENCE.md`
- `DECISIONS.md`
- QA screenshots and reports that prove acceptance.
- Focused test files and scripts.

High-risk staging paths:

- `uv.lock`
- `docker-compose*.yml`
- `docker/api.Dockerfile`
- old phase task deletions
- status-only line ending changes

## Completion Audit

A task is complete only when current evidence proves:

- The requested deliverables exist.
- The relevant tests or checks cover the changed surface.
- Temporary artifacts were removed or intentionally retained.
- OutputMD summary exists.
- The worktree state is either clean after commit or clearly documented with exact remaining paths and reasons.

Do not mark a goal complete based only on intent or partial progress.
