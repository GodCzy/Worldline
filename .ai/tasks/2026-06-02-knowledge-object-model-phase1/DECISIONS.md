# Decisions

更新时间：2026-06-02

## D1: 第一阶段只做表级契约

决定：先落地四个知识对象模型和 EvidenceAnchor 底座，不同时接入解析、chunk、图谱、Wiki 或 UI。

原因：该阶段要先稳定数据链路的可追溯骨架，避免把 parser、retriever 和 UI 的不确定性混入同一批变更。

## D2: 复用现有 schema 管理方式

决定：不引入 Alembic，继续使用 SQLAlchemy `create_all` 和现有兼容 `ALTER TABLE IF EXISTS`。

原因：当前仓库已有 `ensure_knowledge_schema()` 路径，最小变更能降低初始化风险。

## D3: SourceAsset 不替代 KnowledgeFile

决定：`SourceAsset` 表示可版本化来源对象，`KnowledgeFile` 保留为旧文件管理记录，二者通过 `DocumentVersion.file_id` 桥接。

原因：旧上传和文件管理链路仍需可用，第一阶段不做破坏性迁移。
