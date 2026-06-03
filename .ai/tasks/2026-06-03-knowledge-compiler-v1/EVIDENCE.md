# Knowledge Compiler v1 Evidence

更新时间：2026-06-03

## Baseline Freeze

- `git diff --check`：通过；仅有 `.gitattributes` 引起的换行规范化 warning。
- Focused pytest：`26 passed, 1 warning`。
- `npm run docs:build`：通过。
- `npm --prefix web run build`：通过；存在 Vite chunk size warning。
- `docker compose config`：通过，生成 470 行配置。
- Baseline commit：`229f11f chore: freeze worldline restart baseline`。

## Phase 2 Focused Test

命令：

```bash
PYTHONPATH=/mnt/d/dev/Worldline WORLDLINE_SKIP_APP_INIT=1 SAVE_DIR=/tmp/worldline-test-save SILICONFLOW_API_KEY=dummy UV_PROJECT_ENVIRONMENT=/tmp/worldline-min-test-env uv run --no-project --with pytest --with pytest-asyncio --with sqlalchemy --with aiosqlite --with python-dotenv --with colorlog --with pydantic --with pyyaml --with tomli --with tomli-w --with httpx --with fastapi --with loguru --with aiofiles python -m pytest -p no:cacheprovider /mnt/d/dev/Worldline/test/test_document_compiler.py /mnt/d/dev/Worldline/test/test_knowledge_object_repository.py
```

结果：

- 首轮：`1 failed, 7 passed, 1 warning`；失败原因是 image caption 不一定出现在 Markdown，image node char span 应优先定位 `image_ref`。
- 修复后：`8 passed, 1 warning`。

## Pending Final Verification

- `git diff --check`：通过；仅有 `server/routers/knowledge_router.py` 的 LF 规范化 warning。
- Phase 2 + protected backend focused pytest：`28 passed, 1 warning in 6.03s`。
- `npm run docs:build`：通过，VitePress build complete。
- `docker compose config`：通过，生成 470 行配置。
- `python3 -m py_compile server/routers/knowledge_router.py src/knowledge/compiler/models.py src/knowledge/compiler/service.py src/repositories/knowledge_object_repository.py`：通过。
- `npm --prefix web run build`：通过；存在既有 Vite chunk size warning。
- lock 文件核对：`uv.lock`、`pyproject.toml`、npm/pnpm lock 文件无未提交变更。

## Final Commit

- Phase 2 commit：本次提交，最终哈希以 `git log` 和最终总结为准。
