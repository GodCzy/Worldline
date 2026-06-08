# Alignment

日期：2026-06-08

## 目标

推进 P3-1 Evidence-backed LLM Wiki：在知识库详情页增加低噪声 Wiki 阅读面，让真实 Wiki 页面能被浏览、查看 claims、citations、review、open questions、evidence coverage 和 stale 状态。

## 范围

- 前端：`web/src/components/WikiSection.vue`
- 前端 API：`web/src/apis/worldline_api.js`
- 页面入口：`web/src/views/DataBaseInfoView.vue`

## 非目标

- 不改变 Wiki 后端 schema。
- 不改变现有 `/api/knowledge/databases/{db_id}/wiki/*` contract。
- 不引入新依赖。
- 不启用外部 connector。

## 验收

- `test/test_auto_wiki_service.py` 通过，证明 Wiki metadata contract 仍覆盖 claims/citations/review/open questions/evidence coverage。
- 前端 build 通过。
- `/database/:db_id` 有 `LLM Wiki` tab。
- 页面复杂详情通过 drawer 承载，主 tab 保持紧凑。
