# Decisions

- Keep reranker configuration out of create database UI because backend explicitly treats `reranker_config` as deprecated and uses query params after creation.
- Use a payload preview modal instead of inline JSON to preserve a concise create flow.
- Mask Dify token in preview to avoid leaking credentials in screenshots or shared sessions.
