# Worldline Reset Decisions

更新时间：2026-06-03

## Decisions

- 以 `D:\dev\Worldline` 作为唯一活跃工程根目录。
- `D:\document\Worldline` 只保留轻量指针，不保留旧设计 archive。
- 删除旧 Markdown 事实源，允许重建最小必要 Markdown。
- 保留核心代码、测试、Docker、锁文件、环境模板和 `LICENSE`。
- 不重写 Git 历史，不删除 `.git`，不执行 `git reset --hard`。
- 全局 Codex 记忆只通过 ad hoc note 更新，不直接编辑主记忆文件。

## Rationale

旧阶段文档、演示主题和上下文缓存已经干扰后续重构判断。当前重启需要先建立单一事实源，再进入产品设计、架构重构和功能升级。
