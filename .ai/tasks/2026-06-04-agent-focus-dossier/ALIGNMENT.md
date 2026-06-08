# Agent Focus Dossier Alignment

更新时间：2026-06-04

## 目标

在 Agent 工作台中把事件 token drilldown 的目标升级为可审查的 Focus Dossier：点击事件详情 token 后，不只高亮目标，还在 `EVENT DETAIL` 内展示该证据、工具、权限、时间事实或技能候选的结构化信息。

## 范围

- 只修改 `/worldline/agent` 前端视图。
- 复用现有本地 run、Evidence Rail、Tool Trace、Timeline Scrubber、Skill Genome 数据。
- Focus Dossier 展示 title、badge、summary、关键 meta 和关联线索。
- 保持后端 ledger 事件与本地 preview 事件共用同一 token 解析流程。

## 不做

- 不新增后端 API。
- 不修改数据库 schema。
- 不新增依赖。
- 不做跨页面详情页或抽屉。
- 不读取真实证据正文文件内容，只展示当前 payload 已有元数据。

## 验收

- 点击 Evidence token 后出现 Evidence Dossier，包含 source uri、line 范围和关联 graph/timeline 信息。
- 点击 Tool token 后出现 Tool Dossier，包含 permission、status、result 和 branch。
- 点击 Permission token 后出现 Permission Dossier，列出同权限工具调用。
- 点击 Timeline token 后出现 Timeline Dossier，包含 valid from/to、status 和 evidence anchor。
- 点击 Evidence Run token 后出现 Skill Dossier，包含 score、required permissions、evidence run 和 steps。
