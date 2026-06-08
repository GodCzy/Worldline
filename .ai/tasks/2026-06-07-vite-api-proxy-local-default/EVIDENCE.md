# 证据

## 已确认

- `http://127.0.0.1:5050/api/system/health` 返回 200。
- `http://127.0.0.1:5050/api/system/info` 返回 200。
- `http://127.0.0.1:5173/api/system/info` 通过 Vite 代理超时。
- WSL 中 Docker/后端服务正在运行，Vite dev server 也在 WSL 中运行。
- `web/vite.config.js` 未设置 `VITE_API_URL` 时默认代理到 `http://api:5050`。

## 待验证

## 验证结果

### 后端直连

命令：

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:5050/api/system/info -Method Get -TimeoutSec 10
```

结果：返回 `success: true`，说明后端 `/api/system/info` 本身正常。

### Vite 代理

修改前：

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:5173/api/system/info -Method Get -TimeoutSec 10
```

结果：超时。

修改后重启 Vite dev server：

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:5173/api/system/info -Method Get -TimeoutSec 10
```

结果：返回 `True`。

WSL 验证：

```bash
curl -sS -m 10 http://127.0.0.1:5173/api/system/info
```

结果：返回 `{"success":true,...}`。

### Vite dev server

- 清理了旧的根目录 Vite 进程。
- 使用 `.ai/tasks/2026-06-07-vite-api-proxy-local-default/start-vite-dev.sh` 从 `web/` 目录重新启动。
- 当前 5173 上只有一个加载 `web/vite.config.js` 的 Vite 进程。

### 前端构建

命令：

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && /home/joy/.local/bin/npm --prefix web run build"
```

结果：通过。Vite 仍提示既有大 chunk 警告。

### 空白检查

命令：

```powershell
git diff --check -- web/vite.config.js .ai/tasks/2026-06-07-vite-api-proxy-local-default
```

结果：通过。仅提示 `web/vite.config.js` 后续被 Git 触碰时 CRLF 会转 LF。

### 浏览器验证

- 打开 `http://127.0.0.1:5173/` 成功。
- 首页显示后端配置中的 `Living Knowledge OS` 和 `Local-first knowledge workbench...` 文案。
- 页面不再显示“后端暂不可用”或“本地配置”fallback banner。
- 截图：`.ai/tasks/2026-06-07-vite-api-proxy-local-default/screenshots/home-backend-online.png`

### 限制

浏览器插件的控制台日志接口仍保留了旧代理失败时的历史 error/warn；当前代理状态以命令行 5173 请求和刷新后首页 DOM 为准。
