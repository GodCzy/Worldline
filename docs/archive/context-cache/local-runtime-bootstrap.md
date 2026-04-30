# Local Runtime Bootstrap

## Goal
Get the Worldline repository running locally with Docker Compose on this machine.

## Stable Findings
- Date checked: 2026-03-17
- Docker Desktop is healthy and usable on this machine
- A local `.env` was created from the template with a non-empty placeholder model provider key so the backend can boot
- `.env` remains ignored by git and is not committed
- `docker compose up --build -d` now succeeds on this machine
- Verified endpoints:
  - `http://localhost:5050/api/system/health` returns 200
  - `http://localhost:5173` returns 200
- Running services:
  - `api`
  - `worker`
  - `web`
  - `postgres`
  - `redis`
  - `graph`
  - `milvus`
  - `minio`
  - `etcd`

## Local Machine Constraints
- This machine cannot reach `auth.docker.io` reliably
- Build succeeded only after pre-pulling base images from `docker.m.daocloud.io` and tagging them locally:
  - `node:20-alpine`
  - `node:20-slim`
  - `python:3.12-slim`
- `ghcr.io/astral-sh/uv:0.7.2` is reachable directly
- Another local project container, `blueocean-postgres`, occupies host port `5432`

## Local Runtime Overrides
- A local compose override file is present:
  - `docker-compose.override.yml`
- It does two things:
  - remaps Worldline Postgres from host `5432` to host `5433`
  - fixes the Neo4j healthcheck to use `wget` instead of `curl`

## Important Runtime Notes
- The backend boots with a placeholder `SILICONFLOW_API_KEY`
- This is enough for startup and health checks
- Chat, model calls, embedding, reranking, and RAG features still need a real provider key
- API startup logs currently show a PostgreSQL initialization duplicate-key error during table creation, but the service still reaches healthy state and serves requests

## Next Step
- Replace the placeholder model key in local `.env` with a real key
- Then validate real user flows:
  - login
  - homepage
  - theme hub
  - agent chat
  - knowledge base management
