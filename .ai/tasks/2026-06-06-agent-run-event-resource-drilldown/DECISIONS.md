# Decisions

## 2026-06-06

- Reuse `inspectBackendManifestResource` and existing Worldline run APIs; do not add backend endpoints.
- Keep branch/episode/tool/permission/skill tokens local-only until there is a stable backend inspect resource for those exact types.
- Make the backend inspect best-effort after local focus so dossier navigation still works if backend is unavailable.
