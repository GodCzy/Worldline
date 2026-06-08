# Design

## UI Pattern

Use a collapsed `高级后端配置` section below the description and before capability summary.

Default visible fields stay focused: type, name, embedding/LLM/Dify credentials, description.

Advanced section contains:

- 私有知识库 switch: maps to `additional_params.is_private` and private db id prefix.
- 存储标识 input: maps to `additional_params.storage` when set.
- 分块覆盖 switch for non-Dify DBs.
- Chunk parser override controls: `chunk_token_num`, `overlapped_percent`, `delimiter`, `raptor.use_raptor`, `graphrag.use_graphrag`.
- Request preview button: opens a modal with masked payload.

## Contract Notes

- Request stays compatible with `POST /api/knowledge/databases`.
- Deprecated `reranker_config` is not reintroduced; backend stores reranker through query params after creation.
- Dify remains read-only for document add/parse/index flows.
