# Worldline UI Architecture

更新时间：2026-06-03

## Visual Direction

Worldline UI 以黑色背景、青色/金色发光线束、左到右分叉汇聚的世界线为核心视觉。界面应像知识操作台，而不是营销页或普通聊天页。

## First Implementation

- 使用现有 Vue 3、Vite、Pinia、Ant Design Vue。
- 世界线舞台优先用 SVG/Canvas 和现有 G6 资产。
- 先不引入 Three.js/TresJS/Cosmograph。
- Sigma 作为万级节点图谱的性能后备。

## Views

- `/worldline`：控制台。展示模块、问题入口、最近证据、最近 Wiki/Graph/Quality Gate 状态。
- `/worldline/:themeId`：工作台。主舞台展示世界线，右侧或抽屉展示分支详情和下一步。
- `/graph`：管理员图谱页。支持从世界线分支聚焦相关实体和一跳邻居。

## Interactions

- hover：高亮分支路径、证据锚点和相关时间点。
- select：打开证据轨、Wiki 引用、图谱实体和 Agent handoff。
- scrub：时间轴切换证据新增、Wiki 重建、图谱更新和质量门快照。
- handoff：把当前分支上下文交给 Agent，但保留 evidence ids 和审计信息。

## Screenshot Gates

- Desktop：1920x1080、1440x900。
- Mobile：390x844。
- States：empty、loading、error、with branches、hover、selected、evidence rail、handoff。
- Checks：非空画布、文本不重叠、按钮可点、暗色/亮色可读、移动端不溢出。
