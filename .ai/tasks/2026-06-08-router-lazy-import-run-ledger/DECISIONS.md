# Decisions

## 2026-06-08

- 选择改 `server/routers/__init__.py`，而不是让测试用 `importlib.util.spec_from_file_location` 绕过包初始化。原因：包级重导入是结构性问题，影响所有单 router 测试。
- 保留 `from server.routers import router` 兼容路径。原因：`server/main.py` 当前依赖该导入。
- 不改变具体 router 排序和分组，只把“何时导入”从包初始化推迟到完整 API router 构建时。
