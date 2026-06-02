# Phase 10 Document Compiler Phase 2 Cleanup

更新时间：2026-06-02

## 当前阶段

Phase 10：database and knowledge data-chain standardization。

本次完成第二实施片：文档编译器最小闭环与仓库旧身份清理。

## 已落地

- `src/knowledge/compiler/`
  - `CompiledDocument`
  - `CompiledNode`
  - `CompiledEvidenceAnchor`
  - `DocumentCompiler`
- `src/repositories/knowledge_object_repository.py`
  - 持久化 `SourceAsset`
  - 持久化 `DocumentVersion`
  - 持久化 `DocumentNode`
  - 持久化 `EvidenceAnchor`
- `src/knowledge/base.py`
  - `parse_file()` 接入 compiler。
  - 保留旧 `markdown_file` 行为。
  - 在 `processing_params.document_compile` 保存编译摘要。

## 解析策略

- Docling 是支持格式的主解析器。
- PDF 和图片在 Docling 失败后进入 OCR fallback。
- `.md` 和 `.txt` 直接读取，避免基础测试强依赖 Docling。
- 旧 indexing parser 作为兼容 fallback。
- 失败编译保存 `DocumentVersion(status=failed)` 和 parser trace。

## 清理结果

- 删除旧身份、旧演示身份或乱码的历史 Markdown。
- 删除重复 artifact Markdown。
- 修正 3 个 PoE seed JSON 的演示文案。
- 当前旧品牌和旧演示身份扫描无命中。

## 验证基线

- `ruff check`：通过。
- `pytest`：`13 passed, 1 warning`。
- PostgreSQL smoke：通过，真实外键下可写入 `SourceAsset`、`DocumentVersion`、`DocumentNode`、`EvidenceAnchor`。
- `npm run docs:build`：通过，使用 WSL 临时 `npm ci` 后构建，随后删除 `node_modules` 和 build 输出。
- `pnpm --dir web build`：未执行，Windows/WSL 当前均无 `pnpm`，且 `web/` 无 lockfile；本轮没有安装整套前端依赖。
- JSON seed 校验：通过。
- 旧身份扫描：无命中。

## 重要修复

PostgreSQL smoke 暴露了 SQLite 单测未覆盖的 flush 顺序问题：没有 ORM relationship 时，`DocumentNode` 可能先于 `DocumentVersion` flush，导致外键失败。

本轮已在 `KnowledgeObjectRepository` 中对 `SourceAsset` 和 `DocumentVersion` 显式 flush，再写子表。

## 后续边界

下一阶段才处理：

- chunk metadata 绑定 `evidence_ids`。
- EvidenceAnchor 查询 API。
- Evidence UI 或 MCP Server 暴露。
- Milvus、Neo4j、Auto-Wiki 派生产物绑定证据。
