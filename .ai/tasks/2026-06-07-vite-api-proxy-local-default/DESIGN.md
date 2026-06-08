# 设计

## 改动

- `web/vite.config.js` 新增 `apiProxyTarget`：
  - 优先使用 `env.VITE_API_URL`。
  - 未设置时默认 `http://127.0.0.1:5050`，适配当前 WSL/本机前端开发方式。
- Docker Compose 的 web 服务已经显式设置 `VITE_API_URL=http://api:5050`，因此容器内前端仍会走 Docker 网络名。

## 取舍

- 不在前端 API 层硬编码 fallback 后端地址，保持 Vite 代理是开发期网络边界。
- 不改后端 `/api/system/info`，因为直连验证已证明该接口本身返回 200。
