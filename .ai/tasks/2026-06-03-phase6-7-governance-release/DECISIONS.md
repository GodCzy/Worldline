# Decisions

Date: 2026-06-03

## MCP Defaults

Decision: enable only `worldline` by default inside the application MCP registry.

Rationale: Phase 6 requires controlled service-boundary writes, audit logs, and explicit review before enabling external or conditional MCP tools.

## Conditional MCP

Decision: keep `sequentialthinking` and `mcp-server-chart` as conditional configs but disable them by default.

Rationale: they may be useful later, but they are not core Worldline write boundaries and should not be auto-mounted for every Agent.

## Codex Tools

Decision: GitHub and Browser/Playwright stay Codex-side task tools, not application MCP defaults.

Rationale: they are useful for development and QA, but application Agents should not inherit them as runtime write tools.

## Release Gate Shape

Decision: add a static release gate service instead of adding a new dependency or external CI tool.

Rationale: it is deterministic, local, cheap to test, and directly checks the reset-era project evidence.

## Public Demo

Decision: document a local public-demo path without claiming hosted SaaS completion.

Rationale: Phase 7 is a release-readiness milestone, not a production hosting milestone.
