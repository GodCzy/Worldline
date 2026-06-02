# Alignment

更新时间：2026-06-02

## 目标

完成 Worldline Phase 10 的第二实施片：文档编译器最小闭环，并按 Joy 要求清理旧项目身份、冗余 Markdown 和无效归档文件。

## 范围

- 读取 `D:\document\Worldline` 初始化文档、subagent 规则、Skill/MCP 策略和 `.ai/tasks` 证据。
- 使用真实 subagents 做只读映射、QA/MCP 审计和清理审计。
- 新增 compiler service，输出 Markdown、Document AST、EvidenceAnchor 和失败记录。
- 将现有 `parse_file()` 接入 compiler，同时保留旧 `markdown_file` 流程。
- 删除明确旧身份或无效的历史 Markdown，修正活跃 seed 文案。

## 不做

- 不接入前端 UI。
- 不新增 Worldline MCP Server。
- 不重构 LightRAG/Milvus/Neo4j 检索链。
- 不安装新 MCP、Skill 或账号授权。
- 不写入密钥、Token、账号或付费信息。

## 验收标准

- compiler 离线测试覆盖 Docling 主解析、OCR fallback、AST、EvidenceAnchor 和失败记录。
- repository 测试覆盖 `SourceAsset`、`DocumentVersion`、`DocumentNode`、`EvidenceAnchor` 持久化。
- `parse_file()` 集成测试证明旧 Markdown 输出和新编译对象同时存在。
- legacy-pattern 扫描无命中。
- JSON seed 文件仍可解析。
- 任务证据、context-cache 和 `D:\document\OutputMD` 总结已写入。
