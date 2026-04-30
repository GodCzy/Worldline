# AGENTS.md

## Project Identity

Worldline is an enterprise-grade knowledge platform.
It productizes complex domain knowledge into a system for ingestion, retrieval, graph reasoning, agent workflows, and operations.

- Treat this repository as a long-term platform, not a single-module project.
- The current most mature module is Path of Exile (PoE), but PoE is a module, not the platform identity.
- Active identity is `Worldline`; historical evidence may contain legacy naming and must remain auditable.

## Product and Architecture Rules

- Priority order:
  1. Keep runtime stability.
  2. Improve enterprise readiness before broad feature expansion.
  3. Preserve platform-layer vs module-layer separation.
  4. Prefer minimal, local, defensible changes.
  5. Increase observability, operability, and maintainability.
- Platform layer owns branding, routing, shared navigation/layout, permissions, context switching, and operational tooling.
- Module layer owns taxonomy, metadata schema, answer templates, graph schema, recommendation logic, and domain assets.
- Do not hardcode PoE assumptions into shared global modules unless no safer option exists.
- Keep current runtime directories usable until an explicit refactor is approved.
- Do not describe active work as a graduation project or upstream-fork identity in product-facing outputs.
- Canonical active naming is frozen as:
  - Product: `Worldline`
  - Python package: `worldline`
  - Web package: `worldline-web`
  - Docker images: `worldline-api`, `worldline-web`
  - Default database: `worldline_know`

## Execution Model

- Work sequence is mandatory: map first, design second, implement third.
- Use true subagents by default for substantial or cross-cutting tasks.
- Controller responsibilities: task understanding, decomposition, parallelization, consolidation, context-cache updates, and final delivery.
- Default substantial-task wave:
  1. Read-only wave: `system_mapper`, `product_architect`, `qa_release_auditor`
  2. Write wave: `frontend_worker`, `backend_worker`, `knowledge_rag_engineer`, `graph_engineer`, `agent_architect`
- Substantial tasks should usually involve at least two real subagents.
- Trivial tasks may be handled locally without subagents.
- Do not claim a role concluded something unless that subagent actually ran, or clearly mark it as controller synthesis.
- Prefer disjoint write scopes; do not revert others' unrelated edits.
- When stable conclusions emerge, update `docs/context-cache/`.
- If files changed and a stable stop point is reached, run feasible validation and create a git commit unless the user explicitly disables commit.

## Skill and MCP Policy

- MCP and skills are core capabilities, not optional decoration.
- At the start of each substantial phase, judge whether current MCP/skill setup removes recurring friction.
- Priority judgment rules:
  - Long dialogs, cross-phase planning, or handoff compression:
    - Prefer `context-compression` first.
    - Prefer `filesystem-context` first for on-demand file loading and context hygiene.
  - Frontend discovery chain, real-page smoke, route-level verification:
    - Prefer `playwright` skill + Playwright MCP first.
  - CI checks, PR review, release coordination:
    - Prefer GitHub MCP first.
  - Database connection/schema/data inspection and migration verification:
    - Prefer PostgreSQL MCP first.
  - External references, dependency docs, source extraction:
    - Prefer Fetch MCP first.
- Supporting MCPs already available in environment (Notion, Linear, Figma) may be reused when directly useful.
- Add or enable MCPs only for concrete phase value, not novelty.

## Delivery Contract

Every substantial task must end with:

1. changed files
2. why changed
3. how to run/validate
4. remaining risks

Additional mandatory requirements:

- Use Chinese for user-facing progress and summary unless user explicitly requests another language.
- Final response must explicitly include a Chinese section explaining `做出了什么改变`.
- The change explanation must state:
  - which files changed
  - what behavior/text changed
  - what was validated or checked
  - if no file changed, what was inspected/judged and why no change was made
- Provide exactly one suggested next-turn prompt using:
  - `先读：`
  - `当前基线：`
  - `本轮优先任务：`
  - `主控最后汇总：`
  - `要求：`
- For substantial subagent-mode tasks, summarize actual subagent decomposition in final delivery.
- Do not rewrite historical evidence content; isolate it from active reading surface instead.

## Phase Judgment Rule

- At the end of every substantial task, always report:
  - current phase
  - readiness for next phase
  - main remaining gap before advancing
- Judge phase progression proactively; do not wait for user prompt.
- Current reordered progression baseline is:
  - Phase 7: branding and documentation governance refactor
  - Phase 8: multi-module verification and module operational closure
  - Phase 9: backend service-layer refactor and algorithm/runtime optimization
  - Phase 10: database and knowledge data-chain standardization
