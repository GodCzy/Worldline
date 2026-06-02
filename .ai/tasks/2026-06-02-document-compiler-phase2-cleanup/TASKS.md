# Tasks

更新时间：2026-06-02

- [x] 读取 `D:\document\Worldline` 全部 Markdown 和 `.ai/tasks` 初始化证据。
- [x] 读取 `D:\dev\Worldline` 根文档、canonical docs、context-cache 和 Phase 1 证据。
- [x] 启动第二阶段代码映射 subagent。
- [x] 启动 QA/MCP/Skill 审计 subagent。
- [x] 启动 repo cleanup 审计 subagent。
- [x] 新增 `src/knowledge/compiler/`。
- [x] 新增 `KnowledgeObjectRepository`。
- [x] 接入 `KnowledgeBase.parse_file()`。
- [x] 新增 compiler、repository、parse_file 集成测试。
- [x] 清理旧品牌、旧演示身份残留和无效 Markdown。
- [x] 运行 ruff、pytest、JSON 校验和残留扫描。

## 下一步候选

- 将 chunk metadata 与 `evidence_ids` 绑定。
- 新增 compile API 或把现有 parse API 响应扩展为可查询编译版本。
- 将 DocumentNode/EvidenceAnchor 暴露给 Evidence 页面或 MCP Server。
