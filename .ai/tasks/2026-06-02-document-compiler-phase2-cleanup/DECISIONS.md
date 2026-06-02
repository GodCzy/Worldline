# Decisions

更新时间：2026-06-02

## D1: 第二阶段沿旧 parse_file 链路接入

决定：不新增孤立入口，先让现有 `parse_file()` 调用 compiler。

原因：上传、手动解析和可选入库已稳定依赖该入口，最小改动能保证旧 Markdown 链路继续可用。

## D2: compiler 顶层避免重型依赖

决定：Docling、OCR 工厂、MinIO 客户端和旧 indexing parser 都采用懒加载。

原因：AST/Markdown 单元测试不应强制安装 Docling、PyMuPDF、Neo4j、Milvus 或 MinIO 运行时。

## D3: 失败编译也写 DocumentVersion

决定：解析失败时保存 `DocumentVersion(status=failed)` 与 parser trace，不生成节点和证据。

原因：第二阶段要求保留失败记录；失败本身是可审计的编译版本。

## D4: 清理旧身份残留时删除历史无效文档

决定：删除含旧品牌、旧演示身份或乱码的历史 Markdown，并从 legacy index 移除链接。

原因：Joy 本轮明确要求清空旧身份残留和无效 Markdown；保留这些文件会继续污染仓库扫描和文档站归档面。

## D5: 本阶段不安装 MCP/Skill

决定：不安装新 MCP/Skill，不调用 Notion/Figma/Browser/MCP Inspector。

原因：本阶段是后端 compiler 与文件清理；已有本地文件和 WSL/Docker 能力足够。MCP Inspector 要等 Worldline MCP Server 阶段才有价值。
