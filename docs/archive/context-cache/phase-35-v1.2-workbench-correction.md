# phase-35 v1.2 世界线工作台纠偏

## 当前稳定结论

- `v1.2` 的正确方向不再是“世界线界面 / 路线推荐页”
- `v1.2` 的正确方向已经纠偏为：
  - **保留基础聊天界面**
  - **新增世界线工作台 / 世界线画布**
- 工作台不是聊天页上方多几张卡片，而是独立的产品主舞台

## 来自 subagents 的收敛结果

### `system_mapper`

- 当前仓库最适合从 PoE 模块落一个第一版工作台
- 最合理入口是：
  - `/themes/poe -> 世界线工作台 -> /agent 或 /graph`
- 第一版只应复用：
  - 推荐候选
  - 图谱闭环
  - 主题上下文
  - Agent / Graph 承接链

### `product_architect`

- 双界面模型已经成立：
  - 聊天负责提问和持续对话
  - 工作台负责把问题展开成多条世界线
- 第一版必须明确：
  - 多分支
  - 树状结构
  - 风险 / 证据 / 下一步
  - 模块差异化 UI 语法
- 长期方向必须纳入：
  - 用户导入知识库 / 图谱 / 文档
  - 基于基础世界线创建自己的模块

### `frontend_worker`

- 第一版最适合新增专门工作台页，而不是硬塞进现有聊天页
- 最小组件层建议：
  - `WorldlineQuestionBar`
  - `WorldlineBranchCanvas`
  - `WorldlineBranchCard`
  - `WorldlineEvidenceRail`
  - `WorldlineNextStepPanel`
- 状态层建议新增：
  - `worldlineContext`
- 数据适配层建议新增：
  - `poeWorldlineAdapter`
- 可视化第一版最适合：
  - **前端手工 SVG 分支树**
- MCP 负责增强生成与验证，不负责运行时绘制

### `qa_release_auditor`

- 第一版不能沦为普通推荐页
- 最小验收门槛是：
  - 首屏先看到多条世界线
  - 每条线是结构化对象，不是单句推荐
  - 选线后可以带着上下文进入 Agent / Graph
  - 用户一眼能分辨“工作台”与“聊天页”

## 已更新文档

- `README.md`
- `docs/index.md`
- `docs/09-enterprise-evolution-roadmap.md`
- `docs/16-v1.2-planning-baseline.md`
- `docs/18-v1.2-worldline-interface-blueprint.md`

## 当前阶段判断

- 当前阶段：`v1.2 规划`
- readiness：`ready`
- 下一阶段建议：进入 `v1.2` 实施准备

## 进入下一阶段前的主要 gap

当前最主要的 gap 已经不是概念，而是把“世界线工作台 / 世界线画布”进一步压成：

- 页面入口
- 组件树
- 状态层
- 数据适配层
- 页面级验收门槛

也就是：

> 从“方向纠偏完成”进入“可实施前端方案冻结”。
