# 证据

## 修改

- 重写 `web/src/components/SearchConfigModal.vue`。
- 新增 `qa-database-query-params-linkage-cdp.mjs`，使用 mock API 验证知识库详情页检索参数弹窗。

## 验证

### diff check

命令：

```powershell
git diff --check -- web/src/components/SearchConfigModal.vue .ai/tasks/2026-06-07-database-query-params-linkage
```

结果：通过，无输出。

### 前端构建

命令：

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && /home/joy/.local/bin/npm --prefix web run build"
```

结果：通过。Vite 仍提示既有大 chunk 警告。

### CDP QA

命令：

```powershell
& 'C:\Users\Joy\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' .ai/tasks/2026-06-07-database-query-params-linkage/qa-database-query-params-linkage-cdp.mjs
```

结果：通过。

关键 payload：

```json
{
  "search_mode": "hybrid",
  "final_top_k": 10,
  "similarity_threshold": 0.2,
  "keyword_top_k": 50,
  "include_distances": true,
  "metric_type": "COSINE",
  "use_reranker": true,
  "reranker_model": "siliconflow/BAAI/bge-reranker-v2-m3",
  "recall_top_k": 50
}
```

截图：

`D:\dev\Worldline\.ai\tasks\2026-06-07-database-query-params-linkage\screenshots\database-query-params-linkage.png`

## 残余风险

- 当前后端不可用时，页面仍依赖 mock/local 配置才能完整进入详情页；真实联调需要后端服务恢复后再跑一遍同路径。
- Vite 大 chunk 警告为既有问题，本阶段未处理。
