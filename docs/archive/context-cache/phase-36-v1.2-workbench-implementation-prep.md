# phase-36 v1.2 世界线工作台实施准备

## 当前稳定结论

- `v1.2` 的产品方向已经从概念层进入文件级实施准备层。
- 工作台第一版采用：
  - 保留基础聊天界面
  - 新增独立世界线工作台 / 世界线画布
  - 以树状分支结构展示多条世界线

## 来自 subagents 的收敛结果

### `system_mapper`

- 入口应从 [ThemeDetailView.vue](D:/worldline/web/src/views/themes/ThemeDetailView.vue) 出发
- 路由应挂在 [index.js](D:/worldline/web/src/router/index.js) 的 `/themes` 路由组下
- 第一版安全写入面：
  - `web/src/views/worldline/`
  - `web/src/components/worldline/`
  - `web/src/stores/worldlineContext.js`
  - `web/src/data/worldline/poeWorldlineAdapter.js`

### `product_architect`

- 工作台第一版已收敛出：
  - 页面层级
  - 组件树
  - 关键交互流
  - state 设计边界
  - data adapter 设计边界
  - 必须做 / 绝不能做

### `frontend_worker`

- 第一版推荐：
  - 新增 [WorldlineWorkbenchView.vue](D:/worldline/web/src/views/worldline/WorldlineWorkbenchView.vue)
  - 新增 `worldlineContext`
  - 新增 `poeWorldlineAdapter`
  - 用手工 SVG 渲染分支树
- MCP 负责增强生成和验证，不负责运行时绘图

### `qa_release_auditor`

- 第一版最小验收门槛已明确：
  - 首屏先看到路线
  - 路线是结构化对象
  - 选线后可推进到 Agent / Graph
  - 首次使用者能识别这不是普通聊天页

## 本轮新增正式文档

- `docs/19-v1.2-workbench-implementation-prep.md`

## 当前阶段判断

- 当前阶段：`v1.2 规划`
- readiness：`ready`
- 下一阶段建议：进入 `v1.2` 第一波前端实现准备

## 进入下一阶段前的主要 gap

当前主 gap 已经从“概念不清”缩小为：

- 是否按冻结方案真正开始前端实现
- 是否继续严格守住非目标边界
- 是否在实现前确认好第一批文件创建顺序
