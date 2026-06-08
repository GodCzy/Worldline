# Agent Artifact Rail Alignment

更新时间：2026-06-04

## 目标

把上一阶段只存在于事件 token / Focus Dossier 的 Artifact 线索升级为 Agent 工作台右侧可见的 Artifact Rail，让一次 Agent 世界线的产物、路径、来源工具和分支归属可以直接浏览、过滤和定位。

## 范围

- 仅改 Agent 工作台前端和本地 preview 数据的展示/消费逻辑。
- 复用已有 `toolTraces[].artifacts`、`artifactIds` 和后端 event summary 的 `artifactDetails`。
- 保留现有 run ledger API shape，不新增依赖，不新增 DB schema。
- Artifact Rail 必须支持 active branch、selected event、all 三种视角。

## 不做

- 不新增真实文件下载、文件打开、远程 artifact 存储或权限写入。
- 不改变 `WorldlineRunLedgerService` 已有兼容字段。
- 不触碰旧 `.ai/tasks` 删除项和无关 dirty tree。

## 验收

- `/worldline/agent` 右侧出现 Artifact Rail。
- Artifact Rail 能展示数量、视角切换、产物类型、路径、来源工具和分支。
- 点击 Artifact Rail 条目可打开 Focus Dossier，并高亮对应 artifact token / rail 条目。
- 前端 build、diff check 和浏览器验证通过；受限项写入证据。
