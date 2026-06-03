# Worldline Reset Alignment

更新时间：2026-06-03

## 目标

清除 Worldline 旧规划、旧归档、旧演示主题和旧 Agent 记忆文件，把项目事实源重置到 `D:\dev\Worldline`，为后续重新开发、升级优化和重构建立干净基线。

## 成功标准

- `D:\dev\Worldline` 只保留新的最小 Markdown 事实源。
- `D:\document\Worldline` 只保留指向活跃工程的轻量说明。
- 旧 `.ai/tasks`、`docs/archive`、`docs/context-cache`、旧 `.codex`、旧 artifacts 和 PoE demo 残留被清理。
- 核心代码、测试、Docker、锁文件、环境模板和 `LICENSE` 保留。
- 不改变后端 API、数据库 schema、MCP tool contract 或前端路由 contract。

## 不做事项

- 不重写 Git 历史。
- 不删除 `.git`。
- 不执行 `git reset --hard`。
- 不引入新的平台栈或迁移数据库技术。
