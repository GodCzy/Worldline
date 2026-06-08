from __future__ import annotations

import asyncio
import json
import os

from sqlalchemy import or_, select

from server.routers.system_router import load_custom_theme_modules, save_custom_theme_modules
from src.storage.postgres.manager import pg_manager
from src.storage.postgres.models_business import User
from src.storage.postgres.models_knowledge import KnowledgeBase


DB_ID = os.getenv("WORLDLINE_CONTENT_KB_DB_ID", "").strip()
ADMIN_LOGIN = os.getenv("WORLDLINE_CONTENT_KB_ADMIN_LOGIN", "codex_kb_admin").strip()
THEME_ID = os.getenv("WORLDLINE_CONTENT_KB_THEME_ID", "").strip()


async def cleanup() -> dict[str, object]:
    if not DB_ID:
        raise RuntimeError("WORLDLINE_CONTENT_KB_DB_ID is required for cleanup.")

    theme_deleted = False
    if THEME_ID:
        themes = await load_custom_theme_modules()
        kept_themes = [item for item in themes if item.get("id") != THEME_ID]
        theme_deleted = len(kept_themes) != len(themes)
        if theme_deleted:
            await save_custom_theme_modules(kept_themes)

    pg_manager.initialize()
    await pg_manager.ensure_knowledge_schema()
    await pg_manager.ensure_business_schema()

    kb_deleted = False
    admin_deleted = False
    async with pg_manager.get_async_session_context() as session:
        kb_result = await session.execute(select(KnowledgeBase).where(KnowledgeBase.db_id == DB_ID))
        kb = kb_result.scalar_one_or_none()
        if kb is not None:
            await session.delete(kb)
            kb_deleted = True

        user_result = await session.execute(
            select(User).where(or_(User.user_id == ADMIN_LOGIN, User.username == ADMIN_LOGIN)).order_by(User.id.asc())
        )
        user = user_result.scalar_one_or_none()
        if user is not None:
            user.is_deleted = 1
            user.deleted_at = None
            admin_deleted = True

    return {
        "status": "ok",
        "db_id": DB_ID,
        "kb_deleted": kb_deleted,
        "theme_id": THEME_ID,
        "theme_deleted": theme_deleted,
        "admin_login": ADMIN_LOGIN,
        "admin_deleted": admin_deleted,
    }


async def main() -> int:
    try:
        print(json.dumps(await cleanup(), ensure_ascii=False, indent=2))
        return 0
    finally:
        await pg_manager.close()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
