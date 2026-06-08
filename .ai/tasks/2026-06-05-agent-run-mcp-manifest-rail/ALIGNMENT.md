# Alignment

## Goal

把 Agent run 已经分散的 artifacts、gates、evidence、sources、wiki、graph、timeline read contracts 聚合为一个 run 级 MCP manifest，让外部 Agent 先读一个入口就能发现所有可审查资源。

## Scope

- 新增只读 `worldline.inspect_run_manifest`。
- Manifest 返回 run overview、read tools、section counts、resource URI 和可复制 args。
- 前端 Agent Workbench 增加 Run MCP Manifest rail/card，支持一键 Copy MCP。
- 继续复用已有 read tools，不替代 `inspect_run_artifacts/gates/evidence/knowledge`。

## Out Of Scope

- 不新增数据库 schema。
- 不新增写入型 MCP。
- 不改变已有 read tools 的输入输出契约。
- 不做跨 run 搜索或 live DB 查询。

## Acceptance

- Service manifest 包含 `worldline.inspect_run_manifest`，`write_scope: none`，`dispatch_backend: inline`。
- Backend returns sections for `artifacts`, `gates`, `evidence`, `sources`, `wiki`, `graph`, `timeline`.
- Frontend displays a Run MCP Manifest rail/card and copies `worldline.inspect_run_manifest` with `run_id` args.
- Browser QA proves manifest preview includes run URI and at least three read sections.
- Focused tests, Vite build, diff check, and OutputMD summary are recorded.
