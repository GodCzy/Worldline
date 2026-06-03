# Phase 5-7 Knowledge Ops Decisions

Updated: 2026-06-03

## D1. Keep graph extraction deterministic first

Decision: Phase 5 extracts entities, co-mention relationships, and temporal facts from evidence-bound chunks without external LLM calls.

Reason: The immediate requirement is a traceable graph/timeline layer. Deterministic extraction makes tests, smoke checks, and failure replay stable.

## D2. Do not write Neo4j directly yet

Decision: Store graph and temporal artifacts in PostgreSQL first.

Reason: Project rules say external agents must not directly write databases. A controlled local graph contract is safer and can be synced later.

## D3. Publish MCP as a controlled server entrypoint

Decision: Add `src.mcp.worldline_server` and a manifest service instead of installing a high-permission external MCP.

Reason: The project needs a Worldline tool boundary, not full filesystem/database exposure.

## D4. Represent LangGraph and ARQ as explicit workflow metadata

Decision: Persist LangGraph-shaped workflow plans with ARQ dispatch metadata.

Reason: This proves the orchestration contract while avoiding a Redis/worker dependency in unit tests.

## D5. Make Phase 7 gate deterministic and replayable

Decision: Quality gate computes coverage, evidence accuracy, stale pages, permission checks, tracing, cost, latency, and replay payloads locally.

Reason: This creates a production-readiness gate that can run without paid model calls or secrets.
