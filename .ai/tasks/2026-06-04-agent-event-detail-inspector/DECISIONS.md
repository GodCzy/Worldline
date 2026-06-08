# Agent Event Detail Inspector Decisions

更新时间：2026-06-04

## D1. 先做内嵌 Inspector，不做 drawer

右侧 inspector 已是当前 Agent 工作台的审查区，内嵌详情比引入抽屉更轻，且不增加依赖。

## D2. 详情只展示 ID，不做跨服务查询

当前目标是把事件线索显性化。EvidenceAnchor、MCP audit log 和 quality gate run 的深度查询需要后续统一详情契约。
