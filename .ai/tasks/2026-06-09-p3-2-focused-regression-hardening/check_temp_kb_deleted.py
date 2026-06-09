from __future__ import annotations

import asyncio
import json
import os

from sqlalchemy import select

from src.storage.postgres.manager import pg_manager
from src.storage.postgres.models_knowledge import KnowledgeBase


async def main() -> int:
    db_id = os.getenv("CHECK_DB_ID", "").strip()
    if not db_id:
        raise RuntimeError("CHECK_DB_ID is required")

    pg_manager.initialize()
    await pg_manager.ensure_knowledge_schema()
    async with pg_manager.get_async_session_context() as session:
        exists = (
            await session.execute(select(KnowledgeBase.db_id).where(KnowledgeBase.db_id == db_id))
        ).scalar_one_or_none() is not None

    print(json.dumps({"db_id": db_id, "exists": exists}, ensure_ascii=False))
    await pg_manager.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
