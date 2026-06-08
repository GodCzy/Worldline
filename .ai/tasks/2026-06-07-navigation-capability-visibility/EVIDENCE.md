# 证据

## 已确认

- `AppLayout.vue` 当前只在 `userStore.isAdmin` 时把知识图谱、知识库、运营看板放进侧边栏，未登录时确实只剩四个主入口。
- `HomeView.vue` 顶部知识库和图谱按钮也只在管理员状态显示。
- `HomeView.vue` 的“添加自定义模块”仍提示“下一阶段接入”，但主题模块创建弹窗已经在 `/themes?new_module=1` 可用。

## 待验证

## 验证结果

### 前端构建

命令：

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && /home/joy/.local/bin/npm --prefix web run build"
```

结果：通过。Vite 仍提示既有大 chunk 警告。

### 空白检查

命令：

```powershell
git diff --check -- web/src/layouts/AppLayout.vue web/src/views/HomeView.vue .ai/tasks/2026-06-07-navigation-capability-visibility
```

结果：通过。

### 浏览器验证

- 打开 `http://127.0.0.1:5173/themes`，展开侧边栏后能看到：`首页`、`主题分区`、`世界线`、`Agent`、`知识图谱`、`知识库`、`扩展管理`、`运营看板`。
- 未登录锁定项的 aria/tooltip 文案：
  - `Agent · 登录后可用`
  - `知识图谱 · 管理员权限`
  - `知识库 · 管理员权限`
  - `扩展管理 · 最高权限`
  - `运营看板 · 管理员权限`
- 点击锁定 Agent 后跳转到 `http://127.0.0.1:5173/?login=1&redirect=/agent`，首页登录面板可见。
- 首页顶部入口能看到 Agent、知识库和图谱，并显示管理员权限说明。
- 控制台仅出现当前后端 `/api/system/info` 500 和 fallback 日志，未发现新增前端运行错误。
- 截图：`.ai/tasks/2026-06-07-navigation-capability-visibility/screenshots/home-locked-capabilities.png`

### 限制

当前后端仍不可用，因此本轮验证覆盖的是“未登录 + fallback 配置”状态；管理员登录后的真实任务中心、知识库和图谱入口还需后端恢复后再跑一次。
