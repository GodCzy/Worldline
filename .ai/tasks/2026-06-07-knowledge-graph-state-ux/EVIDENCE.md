# 证据

## 修改

- `web/src/components/KnowledgeGraphSection.vue`
  - 增加图谱状态卡：加载中、空图谱、后端降级/错误、知识库类型不支持。
  - 增加紧凑联通摘要：节点/关系统计、接口来源、最后更新时间。
  - 读取 `/api/graph/subgraph` 后补充读取 `/api/graph/stats`，统计失败不阻断主图谱。
- `web/src/components/GraphCanvas.vue`
  - 允许 slot 中标记 `data-graph-interactive` 的状态卡和按钮接收点击事件。
- `web/src/views/GraphView.vue`
  - 全局图谱页空态改为根据当前状态展示后端原因、重试按钮和前往知识库入口。

## 验证

### diff check

命令：

```powershell
git diff --check -- web/src/components/KnowledgeGraphSection.vue web/src/components/GraphCanvas.vue web/src/views/GraphView.vue .ai/tasks/2026-06-07-knowledge-graph-state-ux
```

结果：通过。Git 提示三个前端文件存在 CRLF/LF 工作树换行警告，未做额外换行清理。

### 前端构建

命令：

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && /home/joy/.local/bin/npm --prefix web run build"
```

结果：通过。Vite 仍提示既有大 chunk 警告。

### CDP QA

命令：

```powershell
& 'C:\Users\Joy\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' .ai/tasks/2026-06-07-knowledge-graph-state-ux/qa-knowledge-graph-state-ux-cdp.mjs
```

结果：通过，无 console error。

验证覆盖：

- `/graph?db_id=kb_graph_state` 展示后端降级原因、重新读取和前往知识库按钮。
- `/database/kb_graph_state` 的知识图谱 tab 展示接口来源、节点/关系统计、后端降级状态卡和重试/调整范围按钮。

截图：

- `D:\dev\Worldline\.ai\tasks\2026-06-07-knowledge-graph-state-ux\screenshots\knowledge-graph-global-state.png`
- `D:\dev\Worldline\.ai\tasks\2026-06-07-knowledge-graph-state-ux\screenshots\knowledge-graph-database-state.png`

## 残余风险

- 当前后端暂不可用，本阶段使用 mock 后端验证前端状态机；后端恢复后需要对真实 Neo4j 与真实 LightRAG 各跑一次。
- 本阶段没有修改图谱后端契约，也没有处理 Neo4j 服务本身不可用的根因。
