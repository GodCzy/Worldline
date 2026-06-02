# Phase 3 Evidence Retrieval Evidence

更新时间：2026-06-02

## 已执行验证

### ruff

命令摘要：

```powershell
wsl -d Debian -- bash -lc "cd /tmp && uv run --no-project --index-url https://pypi.org/simple --with ruff ruff check ..."
```

结果：

```text
All checks passed!
```

### pytest

命令摘要：

```powershell
wsl -d Debian -- bash -lc "cd /tmp && WORLDLINE_SKIP_APP_INIT=1 SILICONFLOW_API_KEY=dummy TEST_USERNAME=phase3_admin TEST_PASSWORD=phase3_password PYTHONPATH=/mnt/d/dev/Worldline uv run --no-project --index-url https://pypi.org/simple --with pytest --with pytest-asyncio --with anyio --with httpx --with python-dotenv --with sqlalchemy --with aiosqlite --with tomli --with tomli-w --with pydantic --with colorlog --with loguru --with aiofiles python -m pytest /mnt/d/dev/Worldline/test/test_knowledge_object_models.py /mnt/d/dev/Worldline/test/test_knowledge_object_repository.py /mnt/d/dev/Worldline/test/test_evidence_service.py -q"
```

结果：

```text
13 passed, 1 warning in 3.66s
```

扩展回归：

```text
test_document_compiler.py
test_ragflow_like_chunking.py
test_knowledge_object_models.py
test_knowledge_object_repository.py
test_evidence_service.py
```

结果：

```text
29 passed, 1 warning in 4.36s
```

警告：

- SQLAlchemy `declarative_base()` 迁移警告，属于既有问题。

## 待补验证

- 最终 `git diff --check`。

### PostgreSQL smoke

临时容器：

```text
worldline-phase3-postgres
```

### VitePress docs build

命令摘要：

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm ci && npm run docs:build"
```

结果：

```text
build complete in 19.65s.
```

附注：

- `npm ci` 提示 4 个 moderate vulnerabilities。
- 未执行 `npm audit fix`，避免产生无关依赖变更。
- 构建后已删除 `node_modules` 和 `docs/.vitepress/dist`。

### Router import smoke

尝试过文件级 router import smoke。

结果：

```text
ModuleNotFoundError: No module named 'langchain_community'
```

判断：

- 这是 `knowledge_router.py` 既有顶层依赖链问题，不是本阶段新增依赖。
- 本阶段用 ruff 覆盖新增 route 语法，用服务/仓储测试和 PostgreSQL smoke 覆盖业务契约。
- 未继续安装全量运行依赖，避免把验证扩大成环境重建。

结果摘要：

```text
source_assets=1
document_versions=1
document_nodes=2
evidence_anchors=2
knowledge_chunks=1
chunk_evidence_ids=2
decorated_citations=2
```

清理：

```text
docker rm -f worldline-phase3-postgres
```

结果：

```text
worldline-phase3-postgres
```
