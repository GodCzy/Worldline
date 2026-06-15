# Worldline

Worldline is an Evidence-backed LLM Wiki + Temporal Knowledge Graph OS. It turns documents, web pages, code, evidence, wiki pages, temporal facts, graph relationships, quality gates, MCP tools, and Agent run history into a verifiable knowledge workbench.

It is not a generic RAG chat page. RAG is used as an auxiliary recall layer; the main product surfaces are evidence-grounded Wiki pages, temporal graph reasoning, branchable Worldline views, replayable Agent runs, and controlled external tool access.

## Project Status

Current local development scope is complete through P5.

| Area | Status | Notes |
|---|---|---|
| Baseline knowledge workbench | Mostly complete | KB creation, theme closure, dashboard QA, upload/parse/query linkage, and full-site UI QA are done. Content KB and first-pass graph backend are verified baselines that can keep expanding. |
| P3 Product Core | Done | Evidence-backed LLM Wiki, temporal graph, branch canvas, Agent run ledger/replay, MCP governance, quality gate replay, and compact console UX are implemented and verified. |
| P4 Operational Hardening | Done | Failure evidence, controlled requeue, stale-source rebuild, scoped budgets, admin observability, and cleanup routines are implemented. |
| P5 Local Public Demo | Done | Safe public demo dataset, read-only branch share view, and JSON/Markdown evidence bundle export are implemented. |
| External integrations | Gated | GitHub PR/issue integration and optional Firecrawl/Tavily-style ingestion tools require explicit authorization, secret review, and rollback planning before enablement. |

Accurate completion statement:

- The local P3/P4/P5 feature loop is complete and verified.
- The project is not yet a hosted production SaaS. Production deployment, external connector authorization, long-term SLOs, backup/restore, and real-user operating policies still need a separate release process.

Latest verified checkpoint:

- P5 focused pytest: `9 passed, 1 warning`
- P5 Edge desktop/mobile QA: passed
- Release gate: `12/12` checks passed
- Vite production build: passed
- VitePress docs build: passed
- `docker compose config`: passed

## Core Capabilities

### Evidence Ledger

Worldline preserves source-grounded provenance instead of flattening knowledge into untraceable text. Important objects include:

- `SourceAsset`
- `DocumentVersion`
- `DocumentNode`
- `EvidenceAnchor`
- `KnowledgeChunk`
- `WikiPage`
- `KnowledgeEntity`
- `KnowledgeRelationship`
- `TemporalFact`
- `QualityGateRun`

### LLM Wiki

LLM Wiki is the primary reading surface. It is designed for structured, cited, reviewable knowledge pages with stale/rebuild workflows and quality gate support.

### Temporal Knowledge Graph

The graph layer models entities, relationships, temporal validity, conflicts, and evidence support. It provides graph/timeline focus links and conflict review surfaces.

### Worldline Branch Canvas

The branch canvas visualizes how a root question branches into evidence-supported paths, graph/timeline references, quality gates, and convergence points.

### Agent Run Ledger And Replay

Agent work is persisted as replayable runs, events, artifacts, gate results, evidence references, and run manifests. This makes Agent behavior inspectable rather than hidden in transient chat logs.

### MCP And Skill Governance

External Agent tools are controlled through service boundaries, audit logs, disabled-tool policy, connector review checklists, and rollback guidance. Direct database writes and unrestricted filesystem/admin access are not default behavior.

### Operational Health

Operational health covers queue state, failure evidence, retries, stale source rebuild, scoped budgets, cleanup readiness, and admin action endpoints.

### Public Demo And Evidence Bundles

P5 adds a deterministic read-only public demo:

- Share route: `/worldline/share/demo-branch-evidence`
- Dataset API: `GET /api/worldline/public-demo/dataset`
- Branch share API: `GET /api/worldline/public-demo/branches/{share_id}`
- JSON bundle: `GET /api/worldline/public-demo/evidence-bundle?share_id=demo-branch-evidence&format=json`
- Markdown bundle: `GET /api/worldline/public-demo/evidence-bundle?share_id=demo-branch-evidence&format=markdown`

Public demo endpoints are read-only and do not expose live KB write access, admin actions, MCP writes, GitHub writes, or ingestion connectors.

## Tech Stack

Backend:

- FastAPI
- SQLAlchemy async
- PostgreSQL
- Redis / ARQ
- MinIO
- Milvus
- Neo4j
- LangGraph
- MCP
- Docling / LightRAG / LlamaIndex integration paths

Frontend:

- Vue 3
- Vite
- Pinia
- Ant Design Vue
- G6
- D3
- ECharts
- Graphology / Sigma

Docs and validation:

- VitePress
- pytest
- Ruff
- Docker Compose
- Edge/Browser screenshot QA scripts

## Repository Layout

```text
server/   FastAPI app, routers, middleware
src/      domain services, storage, knowledge compiler, Agent, MCP, configuration
web/      Vue 3 frontend
test/     pytest test suite
docs/     current product and architecture docs
scripts/  migration, release gate, QA, smoke scripts
docker/   Dockerfiles and container support files
.ai/      task evidence, screenshots, decisions, validation reports
```

## Requirements

Recommended local environment:

- Docker Desktop or a compatible Docker Engine
- Docker Compose v2
- Python `>=3.12,<3.14`
- `uv`
- Node.js with `pnpm`
- Git

Optional, depending on the workflows you enable:

- GPU and model assets for full MinerU/PaddleX OCR profiles
- Provider API keys for live LLM, search, or ingestion integrations
- GitHub authorization for PR/issue integration

Do not commit secrets. Keep API keys in `.env` or a secret manager.

## Quick Start With Docker Compose

Clone the repository:

```bash
git clone https://github.com/GodCzy/Worldline.git
cd Worldline
```

Create local environment config:

```bash
cp .env.template .env
```

Edit `.env` if you need model provider keys or non-default service settings. The base stack can be inspected before boot:

```bash
docker compose config
```

Start the default development stack:

```bash
docker compose up -d
```

Default service URLs:

| Service | URL |
|---|---|
| Web app | `http://127.0.0.1:5173` |
| API | `http://127.0.0.1:5050` |
| API health | `http://127.0.0.1:5050/api/system/health` |
| Neo4j browser | `http://127.0.0.1:7474` |
| MinIO console | `http://127.0.0.1:9001` |

Follow the app's first-run flow to initialize the admin user if the database is empty.

Stop the stack:

```bash
docker compose down
```

Start optional OCR/model services only when you have reviewed the resource and GPU requirements:

```bash
docker compose --profile all up -d
```

## Local Development

Install backend dependencies:

```bash
uv sync --all-groups
```

Install frontend dependencies:

```bash
pnpm --dir web install
```

Run the frontend against a local API:

```bash
export VITE_API_URL=http://127.0.0.1:5050
pnpm --dir web dev
```

On Windows PowerShell:

```powershell
$env:VITE_API_URL = "http://127.0.0.1:5050"
pnpm --dir web dev
```

Run docs locally:

```bash
npm run docs:dev
```

Build frontend:

```bash
pnpm --dir web build
```

Build docs:

```bash
npm run docs:build
```

## Validation Commands

Common checks:

```bash
docker compose config
pnpm --dir web build
npm run docs:build
```

Focused backend checks:

```bash
uv run --group test pytest test/test_worldline_public_demo_service.py test/test_worldline_phase6_7_release_gate.py -s
uv run --group test pytest test/test_worldline_operational_health_service.py test/test_worldline_phase6_7_release_gate.py -s
```

Ruff examples:

```bash
uv run --group dev ruff check src/services/worldline_public_demo_service.py src/services/worldline_release_gate_service.py
```

Release gate:

```bash
uv run python scripts/worldline_phase6_7_release_gate.py --output .ai/tasks/release-gate-report.json
```

If your Codex skills live on Windows while running the command in WSL, pass the skills root explicitly:

```bash
uv run python scripts/worldline_phase6_7_release_gate.py \
  --codex-skills-root /mnt/c/Users/Joy/.codex/skills \
  --output .ai/tasks/release-gate-report.json
```

## Public Demo Flow

After starting the stack, open:

```text
http://127.0.0.1:5173/worldline/share/demo-branch-evidence
```

The page demonstrates:

- a deterministic public demo dataset;
- a read-only Worldline branch;
- evidence, wiki, graph, timeline, and gate references;
- JSON and Markdown evidence bundle export;
- replay and rollback information.

This route is intentionally read-only. It is suitable for controlled demonstration, not for granting live admin or write access.

## Security And Integration Boundaries

Worldline treats external tools as controlled integrations:

- GitHub PR/issue workflows require explicit authorization and a recorded rollback path.
- Firecrawl/Tavily-style ingestion tools require source review, data exposure review, and secret handling review.
- MCP servers and tools are governed by allowlists, disabled-tool policy, and audit logs.
- External Agents should write through Worldline services, not directly to databases.
- Secrets must not be written into Markdown, screenshots, repositories, or public URLs.

## Current Documentation

- Product status: `docs/product/worldline-completion-matrix.md`
- Public demo: `docs/product/public-demo.md`
- Product book: `docs/product/worldline-project-book.md`
- Roadmap: `docs/product/worldline-next-roadmap.md`
- Knowledge compiler: `docs/architecture/knowledge-compiler.md`
- LLM Wiki: `docs/architecture/llm-wiki.md`
- Temporal graph: `docs/architecture/temporal-evidence-graph.md`
- Worldline UI: `docs/architecture/worldline-ui.md`
- Agent workflow: `docs/architecture/agent-operating-workflow.md`
- MCP and skill governance: `docs/architecture/mcp-skill-governance.md`
- Operational hardening: `docs/architecture/operational-hardening.md`
- Evaluation gates: `docs/architecture/evaluation-gates.md`

## License

See `LICENSE`.
