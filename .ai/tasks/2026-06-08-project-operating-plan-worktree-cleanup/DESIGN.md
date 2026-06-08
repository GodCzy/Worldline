# 设计

## 文档结构

长期文档：

- `docs/product/worldline-next-roadmap.md`
  - 项目北极星
  - 近期/中期/远期阶段
  - P3 垂直切片
  - 交付证据
  - 不做事项
- `docs/architecture/agent-operating-workflow.md`
  - 主控 Agent 工作流
  - 子代理角色和触发条件
  - local Codex skills 使用矩阵
  - MCP/Browser/GitHub 工具边界
  - 任务目录、验证、提交和回滚规则

任务证据：

- `.ai/tasks/2026-06-08-project-operating-plan-worktree-cleanup/*`
- `D:\document\OutputMD\2026-06-08-Worldline-Project-Operating-Plan-Worktree-Cleanup.md`

## 工作树清理策略

1. 先做只读审计：`git status`、`git diff --name-status`、untracked 文件、可再生产物、潜在密钥。
2. 清理明确可再生产物：browser profile、cache、empty log、build output、临时压缩包等。
3. 保留任务证据、截图、QA 报告和源码变更。
4. 按逻辑包 stage，而不是 `git add .`。
5. 每个 staged 包执行 `git diff --cached --name-status` 和 `git diff --cached --check`。
6. 如果目标要求工作树干净，按清晰提交提交；否则留下清晰 staged/unstaged 报告。

## 子代理使用

本任务使用只读子代理做并行审查：

- 规划/工作流文档缺口审查。
- 工作树清理和提交边界审查。

主控 Agent 负责最终文档、清理、stage/commit 决策和验证。
