# Evidence

更新时间：2026-06-02

## Subagents

- Ampere：第二阶段代码映射，确认落点为 `src/knowledge/base.py`、`src/knowledge/indexing.py`、`src/storage/postgres/models_knowledge.py` 和 repository/compiler 新模块。
- Bernoulli：QA/MCP/Skill 审计，确认本阶段不需要 Browser、Notion、Figma、MCP Inspector；最小测试应覆盖 compiler、fallback、EvidenceAnchor、失败记录和 Postgres smoke。
- Anscombe：cleanup 审计，确认 `D:\document\Worldline` 无旧身份残留，`D:\dev\Worldline` 清理点集中在 archive、context-cache、artifacts 和 3 个 PoE seed JSON。

## Ruff

命令：

```powershell
wsl -d Debian -- bash -lc "cd /tmp && uv run --no-project --index-url https://pypi.org/simple --with ruff ruff check /mnt/d/dev/Worldline/src/knowledge/compiler /mnt/d/dev/Worldline/src/repositories/knowledge_object_repository.py /mnt/d/dev/Worldline/src/knowledge/base.py /mnt/d/dev/Worldline/src/knowledge/__init__.py /mnt/d/dev/Worldline/test/test_document_compiler.py /mnt/d/dev/Worldline/test/test_knowledge_object_repository.py"
```

结果：`All checks passed!`

## Pytest

命令：

```powershell
wsl -d Debian -- bash -lc "cd /tmp && WORLDLINE_SKIP_APP_INIT=1 SILICONFLOW_API_KEY=dummy TEST_USERNAME=phase2_admin TEST_PASSWORD=phase2_password PYTHONPATH=/mnt/d/dev/Worldline uv run --no-project --index-url https://pypi.org/simple --with pytest --with pytest-asyncio --with anyio --with httpx --with python-dotenv --with sqlalchemy --with aiosqlite --with tomli --with tomli-w --with pydantic --with colorlog --with loguru --with aiofiles python -m pytest /mnt/d/dev/Worldline/test/test_document_compiler.py /mnt/d/dev/Worldline/test/test_knowledge_object_repository.py /mnt/d/dev/Worldline/test/test_knowledge_object_models.py -q"
```

结果：`13 passed, 1 warning`。警告来自既有 SQLAlchemy `declarative_base()` deprecation。

## Cleanup Scan

命令：

命令：legacy-pattern scan over active docs, data, source, web, server, and artifacts.

结果：无命中。

命令：academic-writing-term scan over active docs, data, source, web, server, and artifacts.

结果：仅剩 `src/agents/deep_agent/context.py` 和 `src/agents/deep_agent/graph.py` 的通用写作质量规则，不属于旧项目身份。

## JSON Validation

命令：

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && python3 -m json.tool data/poe/processed/cards/item_build/srs-necromancer-league-start.json >/dev/null && python3 -m json.tool data/poe/processed/cards/league_patch/phase1-seed-build-selection.json >/dev/null && python3 -m json.tool data/poe/processed/cards/class_ascendancy/witch-necromancer-overview.json >/dev/null && echo json_ok"
```

结果：`json_ok`

## PostgreSQL Smoke

验证方式：使用 WSL Docker 临时启动 `postgres:16`，执行 `pg_manager.create_tables()` 与 `pg_manager.ensure_knowledge_schema()`，再通过 `KnowledgeObjectRepository.persist_compiled_document()` 写入一份 compiled document。

第一次验证发现真实 PostgreSQL 外键顺序问题：

- `document_nodes.doc_version_id` 写入时对应 `document_versions.doc_version_id` 尚未 flush。
- SQLite 单测没有暴露该问题。

修复：

- 在 `KnowledgeObjectRepository` 中对 `SourceAsset` 和 `DocumentVersion` 显式 `session.flush()` 后再写子表。

最终结果：

```text
{'counts': {'source_assets': 1, 'document_versions': 1, 'document_nodes': 1, 'evidence_anchors': 1}}
```

临时容器 `worldline-phase2-postgres` 验证后已删除。

## Docs Build

Windows 侧没有 `npm`/`pnpm`，改用 WSL Debian。根目录有 `package-lock.json`，因此临时执行：

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm ci && npm run docs:build"
```

结果：VitePress `build complete`。`npm ci` 报 4 个 moderate audit items，本轮没有自动升级依赖。

清理：

- 删除临时 `D:\dev\Worldline\node_modules`
- 删除临时 `D:\dev\Worldline\docs\.vitepress\dist`

## Frontend Build

尝试命令：

```powershell
pnpm --dir web build
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && pnpm --dir web build"
```

结果：

- Windows 侧无 `pnpm`。
- WSL 侧无 `pnpm`。
- `web/` 没有 lockfile，本轮没有临时安装整套前端依赖。
