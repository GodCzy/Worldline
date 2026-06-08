# Alignment

## Goal

把 Agent Workbench 已经渲染的 WikiPage、KnowledgeEntity、TemporalFact 引用升级为 run ledger 的受控 MCP 只读对象，让外部 Agent 能通过 `worldline.inspect_run_knowledge` 检查当前 run 的 wiki、graph、timeline 支撑。

## Scope

- run ledger 保存并列出 `wikiRefs`、`entityRefs`、`timelineRefs`。
- 新增 service/MCP tool：`worldline.inspect_run_knowledge`。
- 前端 Focus Dossier 的 `Wiki`、`Graph`、`Time` 链接支持 `Copy MCP`。
- `makeLedgerPayload()` 显式携带 `wikiRefs`、`entityRefs`、`timelineRefs`。

## Out Of Scope

- 不查询或写入 Postgres knowledge tables。
- 不改 live wiki/graph/timeline API 契约。
- 不新增数据库 migration。
- 不新增写入型 MCP。

## Acceptance

- Manifest 包含 `worldline.inspect_run_knowledge`，`write_scope: none`，`dispatch_backend: inline`。
- Service 支持 `kind` + `item_id` 选择 `wiki`、`graph`、`timeline` 三类对象。
- Frontend Focus Dossier 中 `Wiki`、`Graph`、`Time` 行出现 `Copy MCP`，预览显示正确 tool、URI 和 args。
- Focused pytest、frontend build、diff check、browser QA 通过并记录证据。
