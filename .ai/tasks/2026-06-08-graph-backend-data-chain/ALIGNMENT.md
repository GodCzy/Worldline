# Alignment

日期：2026-06-08

## 目标

从 `D:\document\OutputMD\2026-06-08-Worldline-Next-Goal-Unfinished-Work.md` 继续，优先处理 `/graph` 后端 500 与图谱数据链路。

## 当前范围

- 复现受保护的 `/api/graph/*` 与 Worldline graph/timeline 接口。
- 修复统一图谱路由中 Neo4j/Upload 与 LightRAG 适配器的降级边界。
- 保证 Neo4j 或适配器不可用时，前端得到可解释的降级空图谱，而不是泛化 500。
- 补充 focused tests 与证据记录。

## 非目标

- 不清理当前脏工作树。
- 不迁移数据库 schema。
- 不引入新的图数据库依赖。
- 不把 Worldline 降级为普通 RAG 页面。

## 验收

- `/api/graph/list`、`/api/graph/neo4j/info`、`/api/graph/subgraph`、`/api/graph/stats` 能在真实本地服务中返回可解释状态。
- LightRAG 图谱不因 Upload/Neo4j 的 `graph_base` 不可用而直接失败。
- 适配器创建失败时返回 degraded payload。
- focused pytest 通过。
