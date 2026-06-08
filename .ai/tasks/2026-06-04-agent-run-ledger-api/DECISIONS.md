# Decisions

- Use JSON file persistence for Stage 2 to avoid database schema churn.
- Keep all routes admin-protected.
- Treat Postgres-backed run-ledger tables, SSE streaming, and MCP audit integration as later stages.
- Keep the frontend page independent from backend availability until the API is fully wired into UI actions.
