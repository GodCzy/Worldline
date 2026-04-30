# 世界线 Phase 16 1.0 发布准备

## Goal

- 对当前仓库做一轮 1.0 版本发布前审查。
- 尽可能修复低风险可修复问题。
- 补齐正式测试与验收手册，作为后续版本升级的稳定基线。

## Stable Decisions

- 当前仓库已经达到“毕业设计 1.0 可交付”状态：
  - 本地 Docker 运行链路可启动
  - 首页、主题页、Agent、Graph、后台、文档站可访问
  - PoE 推荐候选、图谱闭环与 Agent 页面上下文联动已具备
- 本轮重点不再扩大功能范围，而是做发布前收口：
  - 修正文档首页乱码
  - 固化 1.0 测试与验收手册
  - 明确当前可测能力、已知边界和后续版本方向
- 外部模型调用仍受第三方 API 额度约束；若出现余额不足或权限错误，属于环境资源问题，不属于 1.0 页面结构缺陷。

## Allowed Files

- `docs/index.md`
- `docs/08-v1.0-test-manual.md`
- `README.md`
- `docs/context-cache/phase-16-v1-release-readiness.md`

## Blocked Files

- 高风险核心层保持不动：
  - `src/knowledge/**`
  - `src/agents/common/**`
  - `src/services/chat_stream_service.py`

## Validation Snapshot

- `pnpm build` in `web/` passed
- `npm run docs:build` passed
- `docker compose ps` shows core services running
- HTTP smoke checks returned `200` for:
  - `/`
  - `/themes`
  - `/themes/poe`
  - `/agent/ChatbotAgent`
  - `/graph`
  - `/api/system/health`
- 登录接口 `/api/auth/token` returned `200`
- 默认智能体接口 `/api/chat/default_agent` returned `200`
- Agent 聊天链路可启动，但当前模型账户余额不足，返回第三方 `403`

## Next Step

- 由用户按 1.0 测试手册进行整轮人工验收。
- 下一版本再根据人工测试结果进入“修问题 -> 优化体验 -> 增强 PoE 能力”的迭代。
