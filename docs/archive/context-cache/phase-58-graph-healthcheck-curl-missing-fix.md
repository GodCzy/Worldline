# Phase 58 - graph unhealthy minimal root-cause fix

## 问题现象

- `docker compose ps` 中 `graph` 长时间为 `unhealthy`。
- `docker inspect graph` 的健康日志连续报错：`/bin/sh: 1: curl: not found`。

## 唯一主阻塞项

- Neo4j 镜像 `neo4j:5.26` 内默认没有 `curl`，但 `graph` 健康检查命令使用了 `curl`。
- 该阻塞属于健康探针工具缺失，不是 Neo4j 进程启动失败；容器日志显示 Neo4j 已正常 `Started`。

## 最小修复面

- 仅调整 graph healthcheck 命令，使用镜像内存在的 `wget`：
  - `docker-compose.yml`
  - `docker-compose.prod.yml`
- 不改业务代码、不改图谱逻辑、不改 API 行为。

## 验证结果

- 仅重建 `graph` 服务：`docker compose up -d graph`
- 验证容器健康检查配置已生效：`docker inspect ... .Config.Healthcheck.Test` 返回 `wget` 命令。
- `docker compose ps graph`：`Up ... (healthy)`
- `docker inspect ... .State.Health`：`Status=healthy`, `FailingStreak=0`
- 主机探测 `http://127.0.0.1:7474` 返回 `200`。

## 阶段判断

- 当前阶段：Phase 4a 条件收口中的运行稳定性补洞。
- 下一阶段就绪度：较前一状态提升；graph 健康阻塞已解除。
- 主要剩余缺口：真实后端登录链路的端到端交互验收证据仍需补齐。

