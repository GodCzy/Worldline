# 证据

## 已确认

- `server/routers/system_router.py` 的 `_normalize_theme_payload` 会合并并保留 `worldline` 子对象额外字段。
- 自定义主题模块通过 `GET/POST/PUT/DELETE /api/system/themes` 管理。
- 前端 `worldline_api.js` 已暴露 Wiki、图谱、时间线、证据、MCP、工作流、Golden Set 和质量门禁能力。

## 待验证

## 验证结果

### 前端构建

命令：

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && /home/joy/.local/bin/npm --prefix web run build"
```

结果：通过。Vite 构建耗时约 4 分 50 秒，仍有既有的大 chunk 警告。

### 空白检查

命令：

```powershell
git diff --check -- web/src/views/themes/ThemeHubView.vue web/src/views/themes/ThemeDetailView.vue web/src/utils/worldlineCapabilities.js .ai/tasks/2026-06-07-theme-module-capability-console
```

结果：通过。仅提示 `ThemeDetailView.vue` 后续被 Git 触碰时 CRLF 会转 LF。

### 浏览器验证

- 打开 `http://127.0.0.1:5173/themes` 成功。
- 点击“添加模块”后，创建弹窗出现“后端能力映射”和“查看保存到后端的模块配置”。
- 未绑定知识库时，弹窗显示“先绑定知识库，模块会自动获得证据、Wiki、图谱、时间线、MCP、工作流和质量门禁入口。”
- 浏览器控制台仅出现后端当前不可用导致的 `/api/system/info` 500 和 fallback 日志，未发现新增前端运行错误。
- 截图：`.ai/tasks/2026-06-07-theme-module-capability-console/screenshots/theme-hub-modal.png`

### 限制

当前本地后端仍返回 500，fallback 配置中没有真实主题模块，因此主题详情页的能力控制台未能在真实模块数据下做浏览器点击验证；该部分已由 Vite 构建覆盖语法和组件编译。
