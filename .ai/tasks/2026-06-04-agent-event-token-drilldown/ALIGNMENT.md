# Agent Event Token Drilldown Alignment

更新时间：2026-06-04

## 目标

让 Agent 工作台 `EVENT DETAIL` 中的事件线索 token 变成可操作入口：点击 Evidence、Tool、Timeline、Permission、Evidence Run 后，在当前页面内切换并高亮对应证据、工具轨迹、时间事实或技能候选。

## 范围

- 修改 `/worldline/agent` 前端交互。
- 为事件详情 token 增加可点击、禁用、已聚焦状态。
- 让 Evidence Rail 支持外部指定 active tab 和 active item。
- 让 Timeline Scrubber 支持高亮指定 temporal fact。
- 让 Tool Trace 和 Skill Genome 支持来自事件详情的高亮。
- 保持 preview 事件和真实 ledger 事件共用同一套解析逻辑。

## 不做

- 不新增后端 API。
- 不修改数据库 schema。
- 不新增前端依赖。
- 不做跨页面深跳或抽屉详情。
- 不处理真实证据正文预览，只定位到现有页面中已存在的目标。

## 验收

- 点击 Evidence token 后 Evidence Rail 切到 Evidence tab 并高亮对应证据。
- 点击 Timeline token 后 Evidence Rail 切到 Time tab，Timeline Scrubber 中对应 temporal fact 高亮。
- 点击 Tool token 后对应 Tool Trace 高亮。
- 点击 Permission token 后相同权限的 Tool Trace 高亮。
- 点击 Evidence Run token 后关联 Skill Genome 候选高亮。
- 不存在目标的 token 显示为不可点击状态。
