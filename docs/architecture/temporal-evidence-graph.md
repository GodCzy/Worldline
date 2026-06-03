# Temporal Evidence Graph Architecture

更新时间：2026-06-03

## Intent

Temporal Evidence Graph 把实体、关系和时间事实变成可追溯、可审查、可投影到 Neo4j 的证据图谱。

## Phase 4 Implementation

- `KnowledgeGraphService` 从 evidence-bound chunks 提取实体、关系和时间事实。
- 每个实体、关系和时间事实都保留 evidence ids。
- metadata 采用 Graphiti 风格：
  - `episode` / `episodes`
  - `provenance`
  - `validity_window`
  - `graphiti_pattern`
- timeline 支持 conflict detection。
- Neo4j 只读 projection 可输出 nodes、relationships、temporal facts 和 Cypher contract。

## Storage Boundary

当前生产写入边界仍是 Worldline service + Postgres evidence graph tables：

- `knowledge_entities`
- `knowledge_relationships`
- `temporal_facts`

Neo4j projection 是只读同步准备，不直接写外部图数据库。

## API

- `POST /api/knowledge/databases/{db_id}/graph/rebuild`
- `GET /api/knowledge/databases/{db_id}/graph/entities`
- `GET /api/knowledge/databases/{db_id}/graph/relationships`
- `GET /api/knowledge/databases/{db_id}/graph/conflicts`
- `GET /api/knowledge/databases/{db_id}/graph/neo4j-projection`
- `GET /api/knowledge/databases/{db_id}/timeline`

