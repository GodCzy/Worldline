# Project Operating Plan And Worktree Cleanup

日期：2026-06-08

## 目标

把 Worldline 后续项目规划、执行工作流、子代理分工、local Codex skills、MCP/Browser/GitHub 使用边界写成长期项目文档，并把当前脏工作树推进到清晰、可验证、可提交的状态。

## 需求拆解

1. 写一份整个项目的后续规划。
2. 定义完善的项目执行工作流。
3. 合理利用多个子代理，但保持一个主控 Agent 决策和改文件。
4. 合理利用 Worldline local skills。
5. 合理利用 MCP、Browser/Playwright、GitHub 等工具，并明确禁用边界。
6. 让仓库工作树变得清晰干净。

## 边界

- `D:\dev\Worldline` 是活跃工程根。
- `D:\document\Worldline` 只作为旧指针，不作为当前事实源。
- 不删除未知用户改动。
- 不用 `git reset --hard` 或 `git checkout --`。
- 不默认启用数据库直写 MCP、全盘 filesystem MCP、shell MCP 或 Docker/Kubernetes admin MCP。
- 提交前必须显式分组、审查 staged 内容和运行最小验证。

## 验收

- 长期规划文档写入 `docs/product/`。
- 工作流/子代理/MCP/skill 操作模型写入 `docs/architecture/`。
- `docs/index.md` 能发现新增文档。
- `.ai/tasks/<task>/EVIDENCE.md` 记录命令、子代理审查、清理和 git 状态。
- 工作树清理有明确证据；若进行提交，提交后 `git status --short --branch` 应清晰。
