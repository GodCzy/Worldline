# Phase 29 - MCP-first 纳入基线与 v1.1 最终验收执行

## 阶段结论

- 当前仍处于 `v1.1` 阶段。
- `v1.1` 的代码与平台基线已经基本 ready 冻结。
- 本轮正式把 MCP 提升为世界线项目的核心能力线之一。
- 当前第一批核心 MCP 固定为：
  - GitHub
  - PostgreSQL
  - Fetch
  - Playwright

## MCP 结论

- 当前 Codex 全局环境里已存在：
  - Notion
  - Linear
  - Figma
  - Playwright
- 本轮新增计划并实际接入配置：
  - GitHub
  - PostgreSQL
  - Fetch
- 其中：
  - Playwright 已纳入第一批核心 MCP，并写入本地 Codex 全局配置
  - GitHub 通过 `gh auth token` + Docker 只读模式接入
  - PostgreSQL 连接本地世界线数据库
  - Fetch 使用本机 Python 环境
  - 新增的 MCP 配置已经写入本地 Codex 配置文件，通常需要重启 Codex 桌面端或新开会话后，新的工具入口才会完整出现在交互环境中

## v1.1 最终验收结论

- 已通过：
  - 登录页
  - PoE 主题页
  - 主题页到 Agent 的推荐链路
  - 主题页到 Graph 的图谱链路
  - Agent 首屏输入区可见
  - 用户头像菜单与系统设置入口可用
  - Dashboard 可访问
- 当前唯一明确阻塞不在代码层，而在外部模型服务：
  - 当前模型调用返回 `403`
  - 原因：账户余额不足

## 阶段判断

- 当前阶段：`v1.1 最终验收执行`
- 对代码基线的判断：`ready 冻结`
- 对完整业务演示的判断：`仍受外部模型额度影响`
- 进入下一阶段前的主要 gap：
  - 决定是否把“模型额度恢复”作为 `v1.1` 最终放行条件
