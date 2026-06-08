from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


API_BASE = os.getenv("WORLDLINE_CONTENT_KB_API_BASE", "http://127.0.0.1:5050").rstrip("/")
ADMIN_LOGIN = os.getenv("WORLDLINE_CONTENT_KB_ADMIN_LOGIN", "codex_kb_admin")
ADMIN_PASSWORD = os.getenv("WORLDLINE_CONTENT_KB_ADMIN_PASSWORD", "")
DB_ID = os.getenv("WORLDLINE_CONTENT_KB_DB_ID", "")
THEME_ID = os.getenv("WORLDLINE_CONTENT_KB_THEME_ID", "")


def _request(
    method: str,
    path: str,
    *,
    token: str | None = None,
    json_body: dict[str, Any] | None = None,
    form_body: dict[str, str] | None = None,
) -> Any:
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
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path} failed: status={exc.code} body={body}") from exc


def _request_optional_delete(path: str, *, token: str) -> None:
    try:
        _request("DELETE", path, token=token)
    except RuntimeError as exc:
        if "status=404" not in str(exc):
            raise


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _theme_payload() -> dict[str, Any]:
    return {
        "id": THEME_ID,
        "name": "Codex Content KB Live Chain",
        "subtitle": "Live evidence-backed Worldline QA",
        "description": "Temporary theme module bound to the P1-3 content KB full-chain validation database.",
        "db_id": DB_ID,
        "knowledge_name": "Codex Content KB Full Chain",
        "knowledge_type": "milvus",
        "knowledge_description": "Temporary QA KB with evidence, wiki, graph, timeline, gate, and Worldline output.",
        "objective": "Validate non-empty KB chain from evidence ledger to Worldline UI.",
        "evidence_sources": ["codex-content-chain.md", "AutoWiki", "GraphService", "QualityGate"],
        "default_question": "How should the evidence-backed Worldline recovery chain be validated?",
        "worldline": {
            "surfaces": {
                "wiki": True,
                "graph": True,
                "timeline": True,
                "quality_gate": True,
                "mcp": True,
                "workflow": True,
            },
            "generation": {
                "mode": "base",
                "branch_budget": 3,
                "quality_profile": "strict",
            },
        },
        "tags": ["codex-qa", "worldline-live", "content-kb"],
    }


def main() -> int:
    if not ADMIN_PASSWORD:
        raise RuntimeError("WORLDLINE_CONTENT_KB_ADMIN_PASSWORD is required")
    if not DB_ID or not THEME_ID:
        raise RuntimeError("WORLDLINE_CONTENT_KB_DB_ID and WORLDLINE_CONTENT_KB_THEME_ID are required")

    login = _request(
        "POST",
        "/api/auth/token",
        form_body={"username": ADMIN_LOGIN, "password": ADMIN_PASSWORD},
    )
    token = str(login.get("access_token") or "")
    _expect(bool(token), "Login did not return access_token")
    _expect(login.get("role") in {"admin", "superadmin"}, f"Unexpected role: {login.get('role')}")

    _request_optional_delete(f"/api/system/themes/{urllib.parse.quote(THEME_ID)}", token=token)
    created_theme = _request("POST", "/api/system/themes", token=token, json_body=_theme_payload())
    _expect(created_theme.get("success") is True, "Theme creation did not return success")
    _expect(created_theme.get("theme", {}).get("id") == THEME_ID, "Created theme id mismatch")

    info = _request("GET", "/api/system/info")
    themes = ((info.get("data") or {}).get("themes") or [])
    theme = next((item for item in themes if item.get("id") == THEME_ID), None)
    _expect(theme is not None, "Theme module is not visible in /api/system/info")
    _expect(theme.get("worldline", {}).get("knowledge_db_id") == DB_ID, "Theme worldline db binding mismatch")

    overview = _request("GET", f"/api/knowledge/databases/{urllib.parse.quote(DB_ID)}/worldline/overview", token=token)
    generated = _request(
        "POST",
        f"/api/knowledge/databases/{urllib.parse.quote(DB_ID)}/worldline/generate",
        token=token,
        json_body={
            "theme_id": THEME_ID,
            "question": "How should the evidence-backed Worldline recovery chain be validated?",
            "context": theme.get("context") or {},
        },
    )
    _expect(overview.get("status") == "ready", f"Overview status mismatch: {overview.get('status')}")
    _expect(generated.get("status") == "ready", f"Generated status mismatch: {generated.get('status')}")

    summary = {
        "status": "ok",
        "api_base": API_BASE,
        "admin_login": ADMIN_LOGIN,
        "admin_role": login.get("role"),
        "db_id": DB_ID,
        "theme_id": THEME_ID,
        "theme_visible_in_info": True,
        "overview_counts": overview.get("counts"),
        "generated": {
            "status": generated.get("status"),
            "branch_count": len(generated.get("branches") or []),
            "quality_status": (generated.get("quality") or {}).get("status"),
            "routeTrace": generated.get("routeTrace"),
        },
        "browser_url": (
            f"http://127.0.0.1:5173/worldline/{THEME_ID}"
            f"?theme={THEME_ID}&module={THEME_ID}&db_id={DB_ID}&knowledge_db_id={DB_ID}"
        ),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
