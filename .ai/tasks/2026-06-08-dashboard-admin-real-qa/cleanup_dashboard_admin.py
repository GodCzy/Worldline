from __future__ import annotations

import asyncio
import json
import os

from sqlalchemy import select

from src.storage.postgres.manager import pg_manager
from src.storage.postgres.models_business import User
from src.utils.datetime_utils import utc_now_naive


ADMIN_LOGIN = os.getenv("WORLDLINE_DASHBOARD_ADMIN_LOGIN", "codex_dash_admin")


async def main() -> int:
    pg_manager.initialize()
    try:
        async with pg_manager.get_async_session_context() as session:
            result = await session.execute(select(User).where(User.user_id == ADMIN_LOGIN))
            user = result.scalar_one_or_none()
            if user is None:
                payload = {"status": "ok", "admin_login": ADMIN_LOGIN, "found": False, "deleted": False}
            else:
                user.is_deleted = 1
                user.deleted_at = utc_now_naive()
                user.reset_failed_login()
                await session.flush()
                payload = {
                    "status": "ok",
                    "admin_login": ADMIN_LOGIN,
                    "found": True,
                    "deleted": bool(user.is_deleted),
                    "id": user.id,
                    "user_id": user.user_id,
                }
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0
    finally:
        await pg_manager.close()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
