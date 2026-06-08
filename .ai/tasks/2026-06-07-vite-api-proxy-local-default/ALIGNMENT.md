# Vite API 代理本地默认值对齐

## 目标

- 修复本机直接运行前端时 `/api/system/info` 通过 Vite 代理超时的问题。
- 保留 Docker Compose 环境里 `VITE_API_URL=http://api:5050` 的显式覆盖。
- 让首页、主题分区和导航状态能在后端已启动时读到真实配置，不再误报 fallback。

## 边界

- 本阶段不修改后端 API、数据库 schema 或鉴权逻辑。
- 只修改前端开发代理默认值和任务记录。
- 不改 Docker Compose 中已存在的 `VITE_API_URL` 显式配置。

## 验收

- 直连 `http://127.0.0.1:5050/api/system/info` 返回 200。
- 通过 Vite 代理 `http://127.0.0.1:5173/api/system/info` 返回 200。
- 首页不再因为代理默认值错误显示本地 fallback 状态。
- 前端构建通过。
