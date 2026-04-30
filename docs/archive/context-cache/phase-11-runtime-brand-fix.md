# 世界线 Phase 11 Runtime Brand Fix

## Goal

- 修复当前前端运行时阻塞问题，恢复登录页与主题页可访问状态。
- 清理浏览器页签中残留的“语析 / Knowledge Management”标题。

## Stable Decisions

- `web/src/data/poePhase1.js` 不再用脆弱的相对路径读取根目录 `data/`，统一改为 Vite 别名 `@poe-data`。
- `web/vite.config.js` 新增 `@poe-data` 别名，并把前端根目录和 PoE 数据目录同时加入 `server.fs.allow`。
- `docker-compose.yml` 的 `web` 服务需要只读挂载 `./data:/data`，否则容器内无法读取 PoE 样本资产。
- `web/index.html` 的浏览器标题统一为“世界线 - Worldline”。

## Allowed Files

- `web/src/data/poePhase1.js`
- `web/vite.config.js`
- `docker-compose.yml`
- `web/index.html`
- `docs/context-cache/phase-11-runtime-brand-fix.md`

## Blocked Files

- `src/knowledge/**`
- `src/agents/common/**`
- `src/services/chat_stream_service.py`
- 其他与本次运行时修复无关的业务层文件

## Validation Snapshot

- `pnpm build` in `web/`: passed
- `GET http://localhost:5173/src/data/poePhase1.js`: `200`
- `GET http://localhost:5173`: returns HTML title `世界线 - Worldline`
- `POST http://localhost:5050/api/auth/token`: login OK
- `docker compose exec web ls /data/poe/processed/cards/manifest.json`: file exists

## Next Step

- 如果前端页面仍有个别交互异常，下一步应该只针对具体页面和控件继续排查，不要再回到大范围方案设计。
