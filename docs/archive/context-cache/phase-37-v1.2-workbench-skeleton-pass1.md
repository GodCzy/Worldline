# phase-37 v1.2 世界线工作台骨架第一波

## 本轮结论

- `v1.2` 第一波前端实现已经启动，并完成了世界线工作台骨架页面。
- 本轮没有重做首页，没有替换基础聊天页，也没有把工作台塞进聊天页侧边栏。
- 工作台保持为独立页面，当前只先支持 `PoE` 模块。

## 本轮实际新增

### 页面与路由

- 新增 `web/src/views/worldline/WorldlineWorkbenchView.vue`
- 在 `web/src/router/index.js` 挂载 `/themes/:themeId/worldline`

### 状态层

- 新增 `web/src/stores/worldlineContext.js`

### 数据适配层

- 新增 `web/src/data/worldline/poeWorldlineAdapter.js`

### 组件层

- 新增 `web/src/components/worldline/WorldlineQuestionBar.vue`
- 新增 `web/src/components/worldline/WorldlineBranchCanvas.vue`
- 新增 `web/src/components/worldline/WorldlineBranchNode.vue`
- 新增 `web/src/components/worldline/WorldlineBranchDetailPanel.vue`
- 新增 `web/src/components/worldline/WorldlineEvidenceRail.vue`
- 新增 `web/src/components/worldline/WorldlineNextStepPanel.vue`

### 入口 CTA

- 最小修改 `web/src/views/themes/ThemeDetailView.vue`
- 当前用户已经可以从 `PoE` 主题详情页进入工作台

## 第一波已经达成的能力

1. 用户可以从 `PoE` 模块进入独立的世界线工作台
2. 工作台首屏先展示问题输入与分支图，而不是聊天框
3. 当前问题会被展开成 `2~3` 条可见世界线
4. 世界线分支已经通过轻量 SVG 树状结构表达
5. 右侧能查看当前分支的说明、证据和下一步动作
6. 选中世界线后，可以继续进入 `Agent`
7. 管理员可继续进入 `Graph`
8. 返回工作台后，当前状态可继续保留在工作台 store 中

## 本轮边界是否守住

守住了。

本轮改动仍然完全处于以下安全写入面内：

- `web/src/views/**`
- `web/src/components/**`
- `web/src/stores/**`
- `web/src/data/**`
- `web/src/router/index.js`

本轮没有进入：

- `src/knowledge/**`
- `src/agents/common/**`
- `src/services/chat_stream_service.py`
- 后端模型与运行链

## 验证基线

本轮已确认：

- `pnpm build` 通过
- `http://localhost:5173/themes/poe/worldline` 返回 `200`
- `http://localhost:5173/themes/poe` 返回 `200`
- Docker 主服务仍在运行

## 下一阶段判断

- 当前阶段：`v1.2 实施`
- readiness：`ready 进入第二波视觉与交互增强`
- 当前最主要 gap：
  - 视觉层还不够“世界线舞台化”
  - 分支树还只是第一版静态布局
  - 右侧面板的信息层次还可以更强
  - 还没有正式做世界线工作台与 Agent / Graph 的更强联动反馈
