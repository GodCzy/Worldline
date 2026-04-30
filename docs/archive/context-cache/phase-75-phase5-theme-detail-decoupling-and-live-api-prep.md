# Phase 75 - Phase 5 Theme Detail Decoupling And Live API Prep

## Summary

- Phase 5 第二轮聚焦两件事：
  - 清理 `ThemeDetailView` 对 `@/data/poePhase1` 的直接依赖。
  - 明确 live API 回归的最小前置条件与命令。
- 本轮不扩业务功能，不改后端路由语义，不改 Phase 4 已冻结的 graph/auth 契约。

## Stable Conclusions

### Remaining `@/data/poePhase1` Direct Imports

1. `web/src/data/worldline/poeWorldlineAdapter.js`

说明：
- 该文件属于模块 adapter 边界，允许继续直接依赖 `poePhase1`。
- `web/src/views/themes/ThemeDetailView.vue` 已不再直接 import `@/data/poePhase1`。

### Boundary Judgment

- 必须继续解耦：
  - `web/src/views/themes/ThemeDetailView.vue`
- 允许保留在模块层：
  - `web/src/data/worldline/poeWorldlineAdapter.js`
- 平台 facade 出口补齐后，主题详情页应只通过 `@/data/worldline` 读取：
  - card title
  - manifest summary
  - recommendation candidates
  - graph loops
  - display label

## Files Changed In This Round

1. `web/src/data/worldline/index.js`
   - 新增 facade 读取出口：
     - `getWorldlineCardTitleById`
     - `getWorldlineManifestSummary`
     - `getWorldlineRecommendationCandidates`
     - `getWorldlineGraphLoops`
2. `web/src/data/worldline/poeWorldlineAdapter.js`
   - 在 PoE adapter 内补齐对应实现，继续把 `poePhase1` 封装在模块边界内。
3. `web/src/views/themes/ThemeDetailView.vue`
   - 改为通过 `@/data/worldline` 取数。
   - 删除本地 `labelMap` 直映射，统一改用 facade 的 display label。
   - 保持 `/themes/:themeId` 行为与主题上下文切换逻辑不变。

## Validation

- 已通过：
  - `pnpm --dir web build`
  - 前端剩余直接依赖扫描：`@/data/poePhase1` 仅剩 `poeWorldlineAdapter.js`
- 未执行：
  - live API integration pytest

## Live API Regression Prep

### Required Preconditions

1. `TEST_BASE_URL`
2. `TEST_USERNAME`
3. `TEST_PASSWORD`
4. API 服务可访问且首管初始化已完成

参考：
- `test/.env.test.example`
- `test/conftest.py`

### Minimal Commands

```powershell
$env:TEST_BASE_URL="http://127.0.0.1:5050"
$env:TEST_USERNAME="..."
$env:TEST_PASSWORD="..."
python -m pytest -q test/api/test_graph_router_list.py test/api/test_unified_graph_router.py -m integration
```

### Pass Criteria

1. 匿名访问 `/api/graph/list`、`/api/graph/neo4j/info` 返回 `401`
2. 普通用户访问上述端点返回 `403`
3. 管理员访问上述端点返回 `200`
4. pytest 退出码为 `0`

## Phase Judgment

- current phase: `Phase 5 / platform-module decoupling and cleanup`
- readiness for next phase: `not ready`
- main remaining gap:
  - 清理剩余模块页面/模块数据层的耦合判断
  - 拿到 `TEST_USERNAME` / `TEST_PASSWORD` 后完成 live API 回归
