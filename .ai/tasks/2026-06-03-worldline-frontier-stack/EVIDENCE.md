# Worldline Frontier Stack Evidence

更新时间：2026-06-03

## Research Evidence

- GitHub API 于 2026-06-03 查询了 Docling、mem0、LlamaIndex、LightRAG、LangGraph、GraphRAG、Playwright MCP、STORM、Graphiti、Letta、Cognee、KAG、Firecrawl MCP、HippoRAG 的 stars、license、updated_at 和 description。
- 子代理只读研究完成了四个方向：前沿知识架构、UX/视觉、Skill/MCP 治理、仓库结构。
- 本地仓库确认现有模型包括 `SourceAsset`、`DocumentVersion`、`DocumentNode`、`EvidenceAnchor`、`WikiPage`、`KnowledgeEntity`、`KnowledgeRelationship`、`TemporalFact`、`QualityGateRun`、`WorldlineMcpAuditLog`。

## Implementation Evidence

- 已写入当前阶段任务目录和新项目/架构文档。
- 已添加编码/换行保护和 Docker context 忽略规则。
- 已调整 live API 测试凭据，使缺少管理员凭据不再阻塞本地单测 collection。
- 已创建本地 Worldline Codex skills，并运行基础校验。
- 已将根 `README.md`、项目级 `AGENTS.md` 和 VitePress `docs/index.md` 指向新的前沿栈事实源。

## Validation Log

- `git status --short --branch`：通过，确认当前分支 `codex/worldline-recovery-refactor`；工作树仍包含重启清理产生的大量计划内删除、既有修改、本轮新增文档和技能外部目录变更。
- `git diff --check`：通过，无 whitespace error；Git 仅提示若干既有文件下次触碰会按 `.gitattributes` LF 化。
- `rg --files -g '*.md' D:\dev\Worldline D:\document\Worldline`：通过，当前 Markdown 入口包含根 README/AGENTS、docs index、新项目书、新架构文档和 `D:\document\Worldline\README.md` 指针。
- Skill validation：6 个本地 skills 使用 `quick_validate.py` 通过，运行方式为 WSL 临时 `uv run --no-project --with pyyaml`，未把 PyYAML 写入项目依赖。
- Skill forward-test：6 个 skills 均由只读子代理完成独立测试，覆盖项目定位、知识管线、后端契约、前端截图 QA、MCP 治理和 release 验证。
- `npm run docs:build`：通过，VitePress 输出 `build complete`，bash 内部确认 `DOCS_EXIT:0`。
- `npm --prefix web run build`：通过，输出 `WEB_EXIT:0`；保留 Vite 大 chunk 警告，主要来自 G6、Ant Design Vue、mindmap、ECharts vendors。
- `docker compose config`：通过，Compose 配置可解析。
- Focused pytest：通过。使用 `/tmp` 临时 uv 环境和最小依赖运行 `test_knowledge_object_models.py`、`test_worldline_live_services.py`、`test_evidence_service.py`，结果 `18 passed, 1 warning in 4.60s`。

## Validation Notes

- 直接使用项目全量 `uv run --group test ...` 会解析 Docling/LlamaIndex/Torch 等重依赖，清华 PyPI 镜像出现 TLS EOF；为避免污染 `uv.lock`，最终采用 `uv run --no-project` + `PYTHONPATH` + 最小依赖的聚焦测试方式验证本次触及面。
- 一次官方 PyPI 索引尝试曾意外改写 `uv.lock` 的 registry URL；已终止残留进程并恢复 `uv.lock`，未保留该副作用。
- 本轮没有执行浏览器截图，因为没有实施 UI 视觉重做；截图门禁已写入文档和 skill，留给后续 UI 实现阶段。
