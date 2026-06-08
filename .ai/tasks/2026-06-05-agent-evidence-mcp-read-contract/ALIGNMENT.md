# Worldline Agent Evidence MCP Read Contract - Alignment

## Goal

把 Agent Workbench 中已有的 EvidenceAnchor / SourceAsset / DocumentNode 详情升级为 run ledger 的受控 MCP 只读对象，让外部 Agent 能通过 `worldline.inspect_run_evidence` 查看证据来源、source URI、行号、sourceRef 和相关 source 节点。

## Scope

- 在 file-backed run ledger 中兼容保存 `evidenceRefs`。
- 新增只读 `list_evidence` 和 `inspect_run_evidence`。
- 新增 MCP tool `worldline.inspect_run_evidence`。
- 前端 Evidence/Source link 增加 `Copy MCP`，并复用 Last MCP Call 预览。
- 不改 Postgres schema，不开放数据库写 MCP，不改变已有 artifact/gate read contract。

## Acceptance

- Manifest 包含 `worldline.inspect_run_evidence`，`write_scope` 为 `none`。
- `inspect_run_evidence(run_id, evidence_id)` 返回 EvidenceAnchor view，包含 `sourceRef`、`sourceUri`、line range 和 URI。
- Source link 可用同一 read contract，通过 `source_id` 选中相关 evidence/source。
- 前端 Focus Dossier evidence/source rows 能复制 MCP read call。
- 后端 focused tests、前端 build、browser QA 通过或记录失败证据。
