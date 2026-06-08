from __future__ import annotations

import asyncio
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from sqlalchemy import select

from src.storage.postgres.manager import pg_manager
from src.storage.postgres.models_business import User
from src.utils.datetime_utils import utc_now_naive


API_BASE = os.getenv("WORLDLINE_E2E_API_BASE", "http://127.0.0.1:5050").rstrip("/")
ADMIN_LOGIN = os.getenv("WORLDLINE_E2E_ADMIN_LOGIN", "codex_temp_admin")
ADMIN_PASSWORD = os.getenv("WORLDLINE_E2E_ADMIN_PASSWORD", "")
RUN_ID = os.getenv("WORLDLINE_E2E_RUN_ID", "")


def _request(
    method: str,
    path: str,
    *,
    token: str | None = None,
    json_body: dict[str, Any] | None = None,
    form_body: dict[str, str] | None = None,
) -> dict[str, Any]:
    headers: dict[str, str] = {}
    data: bytes | None = None
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if json_body is not None:
        data = json.dumps(json_body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if form_body is not None:
        data = urllib.parse.urlencode(form_body).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    request = urllib.request.Request(f"{API_BASE}{path}", data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path} failed: status={exc.code} body={body}") from exc


async def _mark_admin_deleted() -> dict[str, Any]:
    pg_manager.initialize()
    try:
        async with pg_manager.get_async_session_context() as session:
            result = await session.execute(select(User).where(User.user_id == ADMIN_LOGIN))
            user = result.scalar_one_or_none()
            if user is None:
                return {"found": False, "deleted": False}
            user.is_deleted = 1
            user.deleted_at = utc_now_naive()
            user.reset_failed_login()
            await session.flush()
            return {"found": True, "deleted": bool(user.is_deleted), "id": user.id, "user_id": user.user_id}
    finally:
        await pg_manager.close()


async def main() -> int:
    if not RUN_ID:
        raise RuntimeError("WORLDLINE_E2E_RUN_ID is required")
    if not ADMIN_PASSWORD:
        raise RuntimeError("WORLDLINE_E2E_ADMIN_PASSWORD is required")

    login = _request(
        "POST",
        "/api/auth/token",
        form_body={"username": ADMIN_LOGIN, "password": ADMIN_PASSWORD},
    )
    token = str(login.get("access_token") or "")
    if not token:
        raise RuntimeError("Login did not return access_token")

    archived = _request(
        "POST",
        f"/api/worldline/runs/{RUN_ID}/archive",
        token=token,
        json_body={"reason": "codex real E2E cleanup"},
    )
    if archived.get("status") != "archived":
        raise RuntimeError(f"Archive failed for {RUN_ID}: status={archived.get('status')}")

    admin_cleanup = await _mark_admin_deleted()
    print(
        json.dumps(
            {
                "status": "ok",
                "run_id": RUN_ID,
                "run_status": archived.get("status"),
                "latest_event": archived.get("latestEvent", {}).get("eventType"),
                "admin_login": ADMIN_LOGIN,
                "admin_cleanup": admin_cleanup,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
