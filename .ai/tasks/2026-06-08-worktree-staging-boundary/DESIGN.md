# 分组设计

## 数据来源

- `git status --short --branch`
- `git diff --name-status`
- `git ls-files --others --exclude-standard`
- 针对 line-ending/status-only 路径的单独 `git diff`

## 分组维度

1. 已跟踪修改：业务代码、测试、文档、Docker、旧任务证据。
2. 已跟踪删除：旧 phase 任务目录、旧 phase preview 数据、旧测试。
3. 未跟踪任务证据：2026-06-04 到 2026-06-08 的任务目录。
4. 未跟踪业务代码：新增 router/service/test/frontend 文件。
5. 风险项：锁文件、Docker 配置、旧阶段删除、line-ending-only 状态。

## 输出

`worktree-staging-boundary.md` 是主报告，`EVIDENCE.md` 记录命令证据。
