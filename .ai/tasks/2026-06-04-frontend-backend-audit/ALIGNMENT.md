# Frontend Backend Audit

Date: 2026-06-04

## Goal

Audit the current Worldline frontend, backend contracts, and frontend/backend integration after the reset work. Fix focused frontend bugs and integration gaps that can be verified locally.

## Scope

- Frontend routes, views, stores, API clients, shared layout, and Worldline workbench controls.
- Backend FastAPI routers and services that expose knowledge, worldline, wiki, graph, timeline, quality gate, workflow, and MCP capabilities.
- Contract compatibility between frontend payload expectations and backend response shapes.
- Build, static checks, screenshot QA, and feasible local service checks.

## Non Goals

- No broad schema migration unless a blocking bug requires it.
- No new third party frontend dependency unless existing Vue, Pinia, Ant Design Vue, G6, D3, Sigma, Graphology, or ECharts assets cannot solve the issue.
- No rollback of existing uncommitted work from prior Worldline turns.
- No secret, credential, or account initialization changes.

## Acceptance

- Current frontend entry points build successfully.
- Frontend API usage is mapped against protected backend routes.
- Clear list of backend capabilities that the frontend does not yet surface.
- Focused fixes are implemented for confirmed bugs or missing frontend/backend linkage.
- Evidence is recorded in this task directory and a final summary is written to `D:\document\OutputMD`.
