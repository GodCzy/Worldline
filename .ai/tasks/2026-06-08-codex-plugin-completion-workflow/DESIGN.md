# Design

## 文档落点

- `docs/architecture/codex-plugin-inventory.md`：本机 Codex 插件缓存、skills、app connector、适配优先级和风险。
- `docs/product/worldline-completion-matrix.md`：从已完成 P0/P1/P2 到 P3/P4/P5 的完成矩阵。
- `docs/index.md`：新增入口。
- `docs/architecture/mcp-skill-governance.md`：补充 Codex 插件族的默认边界。

## 工作流分层

1. 主控 Agent：读事实源、改代码、提交和最终验收。
2. Local Worldline skills：约束项目身份、后端契约、知识流水线、前端 QA、MCP 治理和 release。
3. Codex 本机插件：Browser/GitHub/OpenAI Developers/Product Design/Data Viz 等按任务启用。
4. External connector：GitHub/Figma/Linear/Notion/OpenAI Platform/Vercel 等需要授权和权限评估。
5. 禁止默认启用项：数据库直写、无限制文件系统、shell/admin/Docker/Kubernetes 写入型 MCP。

## 完成矩阵判定

- Done：代码、测试、截图或任务证据能覆盖验收。
- Verified Baseline：已有证据强，但仍需要进入后续产品切片扩展。
- Partial：已有代码或证据，但验收范围不足。
- Not Started：没有当前证据。
- Blocked By External State：需要账号、权限、外部服务或用户授权。
