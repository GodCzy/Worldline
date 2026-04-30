# Phase 29 - MCP-first capability baseline

## Current judgment

- Worldline now treats MCP as a core operating capability.
- The first useful MCP set for the project is:
  - GitHub
  - PostgreSQL
  - Fetch
  - Playwright
- Existing supporting MCPs in the environment remain useful:
  - Notion
  - Linear
  - Figma

## Install status

- Local Codex config has been updated to include:
  - GitHub MCP as a remote server
  - Fetch MCP via Docker
  - PostgreSQL MCP against the local Worldline Postgres instance
- Playwright is already present in the local Codex config and remains part of the verification stack.

## Policy

- At the start of every substantial phase, the controller should judge whether a new MCP removes real friction.
- Only install or enable MCPs that clearly help with verification, traceability, browser smoke, data inspection, or external source extraction.
- Do not add MCPs for novelty or category completeness alone.

## Phase relation

- Current product phase is still `v1.1`.
- The MCP-first rule does not change the current product phase.
- It changes the operating model used to execute future phases.
