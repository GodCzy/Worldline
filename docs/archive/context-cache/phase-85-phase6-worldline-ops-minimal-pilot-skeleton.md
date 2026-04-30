# Phase 85 - Phase 6 Worldline Ops Minimal Pilot Skeleton

## Summary
- 第二模块试点对象已最终落在 `worldline-ops`。
- Phase 6 第一轮的最小接入骨架已经完成，改动严格限制在主题元数据、worldline adapter 和 facade 注册表。
- 本轮没有触及后端、`worldlineContext` store、router、共享页结构或测试代码。

## Actual Subagent Decomposition
本轮实际并行运行并回收了以下子代理：
- `system_mapper`
  - 结论：第一轮最小必改面只有 3 个点：
    - `src/config/static/info.template.yaml`
    - `web/src/data/worldline/index.js`
    - `web/src/data/worldline/worldlineOpsAdapter.js`
  - `worldlineContext.js`、`router/index.js` 和 themes/worldline 共享页本轮都不应主动改动。
- `product_architect`
  - 结论：试点对象应为 `worldline-ops`，不是 `worldline-sandbox`。
  - 原因：它能更真实地验证“模块发现 + facade 消费 + workbench 生成 + agent handoff”这条链路，同时仍然不需要新的后端协议。
- `backend_worker`
  - 结论：后端保持不动。
  - 当前第二模块发现链路已经由 `/api/system/info` 的静态 YAML 配置承接，不需要扩到 `server/**` 或 `src/knowledge/**`。
- `qa_release_auditor`
  - 结论：验证应同时覆盖：
    - 第二模块可被 `/themes` 和 `/worldline` 发现
    - PoE 路径不回退
    - 共享层不重新读取模块私有结构
- `frontend_worker`
  - 结论：最小接入骨架只需要新增主题元数据、注册 adapter、提供独立 `worldline-ops` adapter。
  - 页面层不需要为第二模块加专用分支。

## Actual Changes
- [src/config/static/info.template.yaml](../../src/config/static/info.template.yaml)
  - 新增 `worldline-ops` 主题元数据。
  - 让 `/themes` 与 `/worldline` 可以从主题配置层发现第二模块。
- [web/src/data/worldline/worldlineOpsAdapter.js](../../web/src/data/worldline/worldlineOpsAdapter.js)
  - 新增 `worldline-ops` 独立 adapter。
  - 提供最小 `buildWorldline()` 产物与共享层已经稳定消费的 facade 方法：
    - `getDisplayLabel`
    - `getManifestSummary`
    - `getRecommendationCandidates`
    - `getRecommendationCandidateById`
    - `getGraphLoops`
    - `getGraphLoopById`
    - `getGraphDefaultKeyword`
    - `getThemeShowcaseMeta`
    - `getThemeShowcaseCandidates`
    - `getThemeShowcaseGraphs`
    - `getAgentContextView`
- [web/src/data/worldline/index.js](../../web/src/data/worldline/index.js)
  - 注册 `worldline-ops` adapter。
  - 使 `hasWorldlineAdapter()`、`resolveWorldlineAdapter()` 和共享 facade 能识别第二模块。

## Discovery And Consumption Chain
### 平台如何发现第二模块
1. `brandApi.getInfoConfig()` 从 `/api/system/info` 拉取信息配置。
2. `useInfoStore.loadInfoConfig()` 将 `themes[]` 规范化为前端消费结构。
3. `ThemeHubView.vue` 直接渲染 `infoStore.themes`，因此主题配置里出现 `worldline-ops` 后，它会自动出现在主题分区。
4. `WorldlineHubView.vue` 在 `themes` 基础上再用 `hasWorldlineAdapter(theme.id)` 过滤可用模块，因此必须同时有：
   - 主题元数据
   - adapter 注册

### 平台如何消费第二模块
1. `/themes/worldline-ops` 通过 `getWorldlineThemeShowcaseMeta/Candidates/Graphs()` 展示模块摘要。
2. `/worldline/worldline-ops` 通过 `resolveWorldlineAdapter(themeId)` 调用 `buildWorldline()` 生成工作台数据。
3. `AgentView.vue` 继续只通过 `getWorldlineAgentContextView()` 读取上下文视图。
4. `GraphView.vue` 继续只通过 `getWorldlineDisplayLabel()`、`getWorldlineGraphLoopById()`、`getWorldlineGraphDefaultKeyword()` 消费模块图谱语义。

## Validation
本轮已完成的验证：
- `pnpm --dir D:\worldline\web build`
  - 通过。
- `npm --prefix D:\worldline run docs:build`
  - 通过。
- 源级边界检查：
  - `web/src/views/**`、`web/src/components/**`、`web/src/stores/**` 中没有重新引入 `@/data/poePhase1`。
  - 共享层没有新增对 `worldlineOpsAdapter` 或 `poeWorldlineAdapter` 的直接页面级 import。
- Node 直接导入 adapter：
  - `worldlineOpsAdapter.id = worldline-ops`
  - `buildWorldline('test question')` 返回：
    - `themeId = worldline-ops`
    - `branches = 3`
    - `activeBranchId = ops-release-gate`
  - `getThemeShowcaseCandidates().length = 3`
  - `getGraphLoops().length = 3`
- Playwright MCP mocked browser smoke：
  - 用真实前端 preview 产物 + mocked `/api/system/info` 验证：
    - `/themes` 页面同时看到 `流放之路` 与 `运营验证`
    - `/themes/worldline-ops` 可进入，标题为 `运营验证`
    - `/worldline` 可看到 `流放之路` 与 `运营验证` 两个模块 pill
    - `/worldline/worldline-ops` 可进入
    - `/themes/poe` 与 `/worldline/poe` 仍可进入

## Current Limitation
- 本机 `http://127.0.0.1:5050/api/system/info` 当前不可连接。
- Docker daemon 也未运行，因此没有完成“真实后端在线 + 浏览器直连后端”的端到端 smoke。
- 这不会推翻本轮最小接入骨架已完成的结论，但意味着还缺一次后端在线后的最终 runtime smoke。

## Phase Judgment
- 当前阶段：`Phase 6 / module pilot implementation`
- readiness for next phase：`ready for backend-linked runtime smoke`
- main remaining gap：`后端 /api/system/info 当前不在线，尚未完成真实后端在线条件下的最终浏览器级发现验证`
