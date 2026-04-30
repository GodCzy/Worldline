---
name: 提交一个启动问题
about: Docker 镜像拉取、服务启动、端口占用等相关问题
title: 'Startup: '
labels: startup
assignees: ''
---

## 1. 问题描述

请清晰描述您在使用 Docker 或启动服务时遇到的问题：

- 操作步骤：您执行了什么操作？
- 预期结果：您希望看到什么？
- 实际结果：实际发生了什么？

例如：执行 `docker compose up -d` 后，`api` 服务一直重启，日志显示无法连接某个依赖服务。

如为世界线仓库问题，请先查看：

- `README.md` 中的运行说明
- `docs/06-platform-operations.md` 中的使用说明

## 2. 环境信息

请提供以下信息，帮助快速定位问题：

- 操作系统：Windows / macOS / Linux 及版本
- Docker 版本：执行 `docker --version`
- Docker Compose 版本：执行 `docker compose version`
- 项目版本：执行 `git rev-parse HEAD`

## 3. 启动命令

请提供您使用的完整启动命令：

```bash
docker compose up -d
```

## 4. 日志信息

请提供相关服务日志，至少包含最近 100 行：

```bash
docker ps
docker compose logs --tail=100
docker logs --tail=100 api
```

将日志粘贴到下方：

```text
# api 日志
...

# 其他相关服务日志
...
```

## 5. 配置文件（可选）

如果您修改过 `docker-compose.yml`、`docker-compose.override.yml` 或 `.env`，请提供相关片段，并注意隐藏敏感信息：

```yaml
# docker-compose 相关片段
...

# .env 相关片段
...
```

## 6. 其他补充

如果已经尝试过以下操作，也请一并说明：

- 是否重启过 Docker Desktop
- 是否清理过旧容器或镜像
- 是否存在代理、防火墙或网络限制
- 是否有截图、报错弹窗或系统日志
