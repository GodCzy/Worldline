# Decisions

## 2026-06-08

- 不把整份 `test/test_worldline_run_ledger_service.py` 作为本阶段唯一验证边界。原因：当前 collection 在 80-180 秒内超时，且本阶段目标是补 `audit_db_id` 写表契约，可以用更窄的 focused test 直接证明。
- 不新增 Postgres run ledger schema。原因：当前 Stage 2 明确是 file-backed ledger，审计表已有 schema。
- 保留 Agent Workbench 本地 preview fallback。原因：后端不可用或未登录时仍需要可解释预览，但文案必须说明真实 API 已存在。
