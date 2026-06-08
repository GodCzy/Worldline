# Evidence

日期：2026-06-08

## 初始证据

- 上一阶段记录 `test/test_worldline_run_ledger_service.py` 在 180 秒内停在 collection。
- `--collect-only` 80 秒内也无 summary。
- `server/routers/__init__.py` 旧实现顶层导入所有 router，并立即构建完整 `router`。

## 修改

- `server/routers/__init__.py` 改为 lazy router spec。
- `create_api_router()` 内部按需 `import_module()`。
- `get_api_router()` 缓存完整 router。
- `__getattr__("router")` 兼容旧导入。

## 待记录

- 子 router import
- 完整 router import
- Run Ledger collect-only
- Run Ledger pytest
- diff check
- OutputMD 总结

## 2026-06-08 交接前补充诊断

- `server.routers.chat_router` import 仍未闭合：`timeout 90s` 后退出。
- 命令：
  `wsl -d Debian --cd /mnt/d/dev/Worldline -- env PYTHONPATH=. WORLDLINE_SKIP_APP_INIT=1 timeout 90s .venv/bin/python -c "import time; s=time.time(); import server.routers.chat_router; print('chat_router ok', round(time.time()-s,3))"`
- 结果：超时；日志只到 `Config file not found` / `requests` dependency warning。
- `faulthandler` 复核显示当前卡点在 `server/routers/chat_router.py` 顶层导入 `src.services.conversation_service`。
- 导入链：`conversation_service.py -> src.agents -> langchain -> transformers -> torch`。
- 已完成的 lazy helper 包括 `agent_manager`、`select_model`、`chat_stream_service`、`agent_run_service`，但仍需继续处理 `conversation_service` 等顶层重型导入。

## 2026-06-08 修复与验证

### 修改

- `server/routers/chat_router.py`
  - 延迟化 `src.services.conversation_service`，避免 router collection 时导入 `src.agents`、LangChain、Transformers、Torch。
  - 延迟化 `src.services.history_query_service`，修复第二轮 `chat_router` import 超时。
- `server/routers/knowledge_router.py`
  - 延迟化 `src.knowledge.indexing`，避免完整 API router import 时因 Docling/Transformers/Torch 卡住。
  - `SUPPORTED_FILE_EXTENSIONS`、`is_supported_file_extension()`、`process_file_to_markdown()` 仍在对应上传/解析 endpoint 调用时按需加载。

### Import 验证

- 命令：
  `wsl -d Debian --cd /mnt/d/dev/Worldline -- env PYTHONPATH=. WORLDLINE_SKIP_APP_INIT=1 timeout 90s .venv/bin/python -c "import time; s=time.time(); import server.routers.chat_router; print('chat_router ok', round(time.time()-s,3))"`
- 结果：`chat_router ok 8.524`。

- 命令：
  `wsl -d Debian --cd /mnt/d/dev/Worldline -- env PYTHONPATH=. WORLDLINE_SKIP_APP_INIT=1 timeout 90s .venv/bin/python -c "import time; s=time.time(); import server.routers.knowledge_router; print('knowledge_router ok', round(time.time()-s,3))"`
- 结果：`knowledge_router ok 41.531`。

- 命令：
  `wsl -d Debian --cd /mnt/d/dev/Worldline -- env PYTHONPATH=. WORLDLINE_SKIP_APP_INIT=1 timeout 180s .venv/bin/python -c "import time; s=time.time(); from server.routers import router; print('api router ok', len(router.routes), round(time.time()-s,3))"`
- 结果：`api router ok 206 48.806`。

### Run Ledger 测试

- 命令：
  `wsl -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && timeout 120s env PYTHONPATH=. WORLDLINE_SKIP_APP_INIT=1 .venv/bin/pytest --collect-only test/test_worldline_run_ledger_service.py -q'`
- 结果：`7 tests collected in 2.85s`。

- 命令：
  `wsl -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && timeout 240s env PYTHONPATH=. WORLDLINE_SKIP_APP_INIT=1 .venv/bin/pytest test/test_worldline_run_ledger_service.py test/test_worldline_run_audit_contract.py -q -vv'`
- 结果：`8 passed, 1 warning in 5.72s`。

### Diff 与进程检查

- 命令：
  `git diff --check -- server/routers/__init__.py server/routers/chat_router.py server/routers/knowledge_router.py test/test_worldline_run_ledger_service.py test/test_worldline_run_audit_contract.py .ai/tasks/2026-06-08-router-lazy-import-run-ledger .ai/tasks/2026-06-08-agent-run-ledger-audit-contract`
- 结果：通过；仅提示 `server/routers/chat_router.py`、`server/routers/knowledge_router.py` 的既有 CRLF/LF warning。

- 命令：
  `wsl -d Debian -- pgrep -af pytest`
- 结果：无残留 pytest 进程。
