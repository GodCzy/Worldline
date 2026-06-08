# Worldline Reset Design

更新时间：2026-06-03

## 清理设计

- 删除旧 Markdown 内容来源，再重建 `README.md`、`AGENTS.md`、`docs/index.md` 和本任务目录。
- 删除旧项目内记忆与归档：`.ai/tasks`、`.codex`、`docs/archive`、`docs/context-cache`。
- 删除旧证据与演示残留：`artifacts`、legacy demo data、旧 Worldline demo adapter。
- 保留工程边界：`server`、`src`、`web`、`test`、`docker`、`scripts`。

## 文档设计

- 根 `README.md` 只记录启动、验证、目录和重构原则。
- 根 `AGENTS.md` 只记录项目级 Agent 规则和事实源边界。
- `docs/index.md` 作为 VitePress 的最小文档站首页。
- `D:\document\Worldline\README.md` 只作为指向活跃工程的说明。

## 验证设计

- 文件核对：Markdown 列表、旧引用搜索、Git 状态。
- 工程核对：Docker Compose config、前端构建、VitePress 构建、关键 pytest。
- 证据记录：本目录 `EVIDENCE.md` 和 `D:\document\OutputMD\2026-06-03-worldline-reset.md`。
