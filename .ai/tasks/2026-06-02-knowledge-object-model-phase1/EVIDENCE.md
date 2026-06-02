# Evidence

更新时间：2026-06-02

## 离线测试

命令：

```powershell
wsl -d Debian -- bash -lc "cd /tmp && WORLDLINE_SKIP_APP_INIT=1 SILICONFLOW_API_KEY=dummy TEST_USERNAME=phase1_admin TEST_PASSWORD=phase1_password PYTHONPATH=/mnt/d/dev/Worldline uv run --no-project --index-url https://pypi.org/simple --with pytest --with pytest-asyncio --with anyio --with httpx --with python-dotenv --with sqlalchemy --with tomli --with tomli-w --with pydantic --with colorlog --with loguru python -m pytest /mnt/d/dev/Worldline/test/test_knowledge_object_models.py -q"
```

结果：`6 passed, 1 warning`。警告来自既有 `models_business.py` 的 SQLAlchemy 2.0 `declarative_base()` deprecation。

## Ruff

命令：

```powershell
wsl -d Debian -- bash -lc "cd /tmp && uv run --no-project --index-url https://pypi.org/simple --with ruff ruff check /mnt/d/dev/Worldline/src/storage/postgres/models_knowledge.py /mnt/d/dev/Worldline/src/storage/postgres/manager.py /mnt/d/dev/Worldline/test/test_knowledge_object_models.py"
```

结果：`All checks passed!`

## Diff 检查

命令：

```powershell
git diff --check
```

结果：通过。Git 提示两个已跟踪文件未来可能按工作树规则从 LF 转为 CRLF。

## PostgreSQL Schema Smoke

验证方式：使用 WSL Docker 临时启动 `postgres:16`，执行 `pg_manager.create_tables()` 与 `pg_manager.ensure_knowledge_schema()`，再查询 `information_schema` 与 `pg_indexes`。

结果：

- 新增表存在：`source_assets`、`document_versions`、`document_nodes`、`evidence_anchors`。
- `metadata` 数据库列为 `jsonb`。
- 关键索引存在，包括 `idx_source_assets_db_type`、`idx_document_versions_asset_status`、`idx_document_nodes_version_order`、`idx_evidence_anchors_doc_node`。
- 临时容器验证后已删除。
