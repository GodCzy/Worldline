# Phase 62 - readonly QA graph/auth script baseline

## Baseline

- 本轮目标：仅补“只读验收脚本入口 + 使用文档”，不改业务逻辑源码。
- 变更范围：`scripts/` 与 `docs/`。

## 落地结果

1. 新增脚本：`scripts/qa_graph_auth_readonly_check.py`
   - 默认只读（仅 GET）
   - 默认不登录、不造数
   - 可选传入 `admin/user` token 做正负例
   - 输出状态码与关键 URL 到 `artifacts/qa-readonly-graph-auth-<timestamp>/`
2. 新增文档：`docs/21-readonly-qa-graph-auth-script.md`
   - 说明脚本用途与运行方式
   - 说明 artifact 结构
   - 说明 MCP Playwright 复核步骤
   - 明确临时用户风险与默认关闭策略

## 验证

- 执行：`python scripts/qa_graph_auth_readonly_check.py --self-check`
- 结果：脚本可执行，artifact 输出成功，未触发网络写入行为。

## Phase Judgment

- 当前阶段：Phase 4b 验收可追溯性增强（只读验收工具化）
- 下一阶段就绪度：高（可直接被 QA/发布流程复用）
- 主要剩余缺口：将该脚本纳入统一 smoke 入口（继续保持只读）
