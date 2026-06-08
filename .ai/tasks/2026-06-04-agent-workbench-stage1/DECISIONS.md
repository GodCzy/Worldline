# Decisions

- Stage 1 ships an inspectable local Agent Workbench before persistent backend run-ledger storage.
- The view reuses the existing Worldline canvas and evidence components instead of introducing a new graph library.
- The route is `/worldline/agent`; theme-specific workbench routes remain `/worldline/:themeId`.
- Future backend endpoints are represented as API wrappers, but unavailable endpoints must not break the local workbench.
