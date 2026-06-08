"""Create or update a local Worldline superadmin account.

Required environment variables:
- POSTGRES_URL
- WORLDLINE_SUPER_ADMIN_NAME
- WORLDLINE_SUPER_ADMIN_PASSWORD

Optional:
- WORLDLINE_SUPER_ADMIN_USER_ID
- WORLDLINE_SUPER_ADMIN_PHONE
"""

import asyncio
import json
import os
import re
import sys

from sqlalchemy import or_, select

from server.utils.auth_utils import AuthUtils
from src.storage.postgres.manager import pg_manager
from src.storage.postgres.models_business import Department, User


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is required.")
    return value


def _validate_user_id(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_]{3,20}", value):
        raise RuntimeError("WORLDLINE_SUPER_ADMIN_USER_ID must be 3-20 chars: letters, numbers, underscore.")
    return value


async def ensure_superadmin() -> dict[str, object]:
    username = _required_env("WORLDLINE_SUPER_ADMIN_NAME")
    password = _required_env("WORLDLINE_SUPER_ADMIN_PASSWORD")
    user_id = _validate_user_id(os.getenv("WORLDLINE_SUPER_ADMIN_USER_ID", username).strip() or username)
    phone_number = os.getenv("WORLDLINE_SUPER_ADMIN_PHONE", "").strip() or None

    pg_manager.initialize()
    await pg_manager.create_business_tables()
    await pg_manager.ensure_business_schema()

    async with pg_manager.get_async_session_context() as session:
        dept_result = await session.execute(select(Department).where(Department.name == "默认部门"))
        department = dept_result.scalar_one_or_none()
        if department is None:
            department = Department(name="默认部门", description="Worldline default department")
            session.add(department)
            await session.flush()

        existing_result = await session.execute(
            select(User)
            .where(or_(User.user_id == user_id, User.username == username))
            .order_by(User.id.asc())
        )
        matches = existing_result.scalars().all()
        if len(matches) > 1:
            raise RuntimeError("Multiple users match the requested username/user_id; resolve the conflict manually.")

        password_hash = AuthUtils.hash_password(password)
        action = "created"

        if matches:
            user = matches[0]
            user.username = username
            user.user_id = user_id
            user.password_hash = password_hash
            user.role = "superadmin"
            user.phone_number = phone_number
            user.department_id = department.id
            user.is_deleted = 0
            user.deleted_at = None
            user.reset_failed_login()
            action = "updated"
        else:
            user = User(
                username=username,
                user_id=user_id,
                phone_number=phone_number,
                avatar=None,
                password_hash=password_hash,
                role="superadmin",
                department_id=department.id,
                is_deleted=0,
            )
            session.add(user)
            await session.flush()

        await session.flush()

        return {
            "action": action,
            "id": user.id,
            "username": user.username,
            "user_id": user.user_id,
            "role": user.role,
            "department_id": user.department_id,
            "password_verified": AuthUtils.verify_password(user.password_hash, password),
        }


async def main() -> int:
    try:
        result = await ensure_superadmin()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    finally:
        await pg_manager.close()


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(main()))
    except Exception as exc:
        print(f"ensure_superadmin failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
