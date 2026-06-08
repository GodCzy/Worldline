from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


API_BASE = os.getenv("WORLDLINE_DASHBOARD_API_BASE", "http://127.0.0.1:5050").rstrip("/")
ADMIN_LOGIN = os.getenv("WORLDLINE_DASHBOARD_ADMIN_LOGIN", "codex_dash_admin")
ADMIN_PASSWORD = os.getenv("WORLDLINE_DASHBOARD_ADMIN_PASSWORD", "")


def _request(
    method: str,
    path: str,
    *,
    token: str | None = None,
    form_body: dict[str, str] | None = None,
) -> Any:
    headers: dict[str, str] = {}
    data: bytes | None = None
    if token:
        headers["Authorization"] = f"Bearer {token}"
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


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    if not ADMIN_PASSWORD:
        raise RuntimeError("WORLDLINE_DASHBOARD_ADMIN_PASSWORD is required")

    login = _request(
        "POST",
        "/api/auth/token",
        form_body={"username": ADMIN_LOGIN, "password": ADMIN_PASSWORD},
    )
    token = str(login.get("access_token") or "")
    _expect(bool(token), "Login did not return access_token")
    _expect(login.get("role") in {"admin", "superadmin"}, f"Unexpected role: {login.get('role')}")

    endpoints = {
        "stats": "/api/dashboard/stats",
        "users": "/api/dashboard/stats/users",
        "tools": "/api/dashboard/stats/tools",
        "knowledge": "/api/dashboard/stats/knowledge",
        "agents": "/api/dashboard/stats/agents",
        "timeseries": "/api/dashboard/stats/calls/timeseries?type=models&time_range=14days",
        "conversations": "/api/dashboard/conversations?status=active&limit=8&offset=0",
        "feedbacks": "/api/dashboard/feedbacks?rating=all",
    }

    responses = {name: _request("GET", path, token=token) for name, path in endpoints.items()}

    _expect(isinstance(responses["stats"], dict), "stats response must be an object")
    _expect(isinstance(responses["users"], dict), "users response must be an object")
    _expect(isinstance(responses["tools"], dict), "tools response must be an object")
    _expect(isinstance(responses["knowledge"], dict), "knowledge response must be an object")
    _expect(isinstance(responses["agents"], dict), "agents response must be an object")
    _expect(isinstance(responses["timeseries"], dict), "timeseries response must be an object")
    _expect(isinstance(responses["conversations"], list), "conversations response must be a list")
    _expect(isinstance(responses["feedbacks"], list), "feedbacks response must be a list")

    summary = {
        "status": "ok",
        "api_base": API_BASE,
        "admin_login": ADMIN_LOGIN,
        "admin_role": login.get("role"),
        "stats_keys": sorted(responses["stats"].keys()),
        "user_totals": {
            "total_users": responses["users"].get("total_users"),
            "active_users_24h": responses["users"].get("active_users_24h"),
            "active_users_30d": responses["users"].get("active_users_30d"),
        },
        "tool_totals": {
            "total_calls": responses["tools"].get("total_calls"),
            "successful_calls": responses["tools"].get("successful_calls"),
            "failed_calls": responses["tools"].get("failed_calls"),
        },
        "knowledge_totals": {
            "total_databases": responses["knowledge"].get("total_databases"),
            "total_files": responses["knowledge"].get("total_files"),
            "total_nodes": responses["knowledge"].get("total_nodes"),
        },
        "agent_total": responses["agents"].get("total_agents"),
        "timeseries_keys": sorted(responses["timeseries"].keys()),
        "conversation_count": len(responses["conversations"]),
        "feedback_count": len(responses["feedbacks"]),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
