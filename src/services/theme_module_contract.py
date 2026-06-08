from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from typing import Any

THEME_MODULE_SOURCE = "custom-theme-module"
WORLDLINE_SURFACE_KEYS = ("wiki", "graph", "timeline", "quality_gate", "mcp", "workflow")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_string(value: Any, default: str = "") -> str:
    if value is None:
        return default
    normalized = str(value).strip()
    return normalized if normalized else default


def normalize_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    return bool(value)


def normalize_string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        source = value
    elif isinstance(value, str):
        source = [item.strip() for item in value.split(",")]
    else:
        source = []
    return [str(item).strip() for item in source if str(item).strip()]


def normalize_surface_map(value: Any) -> dict[str, bool]:
    source = value if isinstance(value, dict) else {}
    result = {key: bool(source.get(key, True)) for key in WORLDLINE_SURFACE_KEYS}
    for key, item in source.items():
        if key not in result and isinstance(item, bool):
            result[str(key)] = item
    return result


def safe_theme_id(value: Any) -> str:
    candidate = normalize_string(value).lower()
    candidate = re.sub(r"[^a-z0-9_-]+", "-", candidate)
    candidate = re.sub(r"-{2,}", "-", candidate).strip("-_")
    return candidate[:80] or f"module-{uuid.uuid4().hex[:8]}"


def extract_theme_db_id(theme: dict[str, Any]) -> str:
    context = theme.get("context") if isinstance(theme.get("context"), dict) else {}
    worldline = theme.get("worldline") if isinstance(theme.get("worldline"), dict) else {}
    knowledge = theme.get("knowledge") if isinstance(theme.get("knowledge"), dict) else {}
    metadata = theme.get("metadata") if isinstance(theme.get("metadata"), dict) else {}
    return normalize_string(
        theme.get("db_id")
        or theme.get("knowledge_db_id")
        or worldline.get("db_id")
        or worldline.get("knowledge_db_id")
        or context.get("db_id")
        or context.get("knowledge_db_id")
        or knowledge.get("db_id")
        or knowledge.get("knowledge_db_id")
        or metadata.get("db_id")
        or metadata.get("knowledge_db_id")
    )


def normalize_theme_payload(
    payload: dict[str, Any],
    *,
    existing: dict[str, Any] | None = None,
    fixed_id: str | None = None,
) -> dict[str, Any]:
    existing = existing or {}
    source = {**existing, **(payload or {})}
    metadata = existing.get("metadata") if isinstance(existing.get("metadata"), dict) else {}
    source_metadata = source.get("metadata") if isinstance(source.get("metadata"), dict) else {}
    context = source.get("context") if isinstance(source.get("context"), dict) else {}
    worldline = source.get("worldline") if isinstance(source.get("worldline"), dict) else {}
    knowledge = source.get("knowledge") if isinstance(source.get("knowledge"), dict) else {}
    links = source.get("links") if isinstance(source.get("links"), dict) else {}

    theme_id = fixed_id or safe_theme_id(source.get("id") or source.get("name") or source.get("title"))
    name = normalize_string(source.get("name") or source.get("title"), "自定义知识模块")
    db_id = extract_theme_db_id(source)
    knowledge_name = normalize_string(
        source.get("knowledge_name")
        or source.get("database_name")
        or knowledge.get("name")
        or metadata.get("knowledge_name")
    )
    knowledge_type = normalize_string(
        source.get("knowledge_type")
        or source.get("kb_type")
        or knowledge.get("type")
        or knowledge.get("kb_type")
        or metadata.get("knowledge_type")
    )
    knowledge_description = normalize_string(
        source.get("knowledge_description")
        or knowledge.get("description")
        or metadata.get("knowledge_description")
    )
    objective = normalize_string(
        source.get("objective")
        or worldline.get("objective")
        or context.get("objective")
        or knowledge.get("objective"),
        "围绕绑定知识库生成可验证的世界线。",
    )
    evidence_sources = normalize_string_list(
        source.get("evidence_sources")
        or worldline.get("evidence_sources")
        or context.get("evidence_sources")
        or knowledge.get("evidence_sources")
    )
    default_question = normalize_string(
        source.get("default_question")
        or worldline.get("default_question")
        or context.get("default_question"),
        "围绕这个知识库生成一条可验证的世界线，并指出证据、图谱关系和待确认分支。",
    )
    surfaces = worldline.get("surfaces") if isinstance(worldline.get("surfaces"), dict) else {}
    capability_map = worldline.get("capability_map") if isinstance(worldline.get("capability_map"), dict) else {}
    generation = worldline.get("generation") if isinstance(worldline.get("generation"), dict) else {}
    source_generation = source.get("generation") if isinstance(source.get("generation"), dict) else {}
    context_generation = context.get("generation") if isinstance(context.get("generation"), dict) else {}
    normalized_generation = {**context_generation, **generation, **source_generation}
    if "mode" not in normalized_generation:
        normalized_generation["mode"] = normalize_string(source.get("generation_mode"), "base")
    if "branch_budget" not in normalized_generation:
        normalized_generation["branch_budget"] = source.get("branch_budget") or 3
    if "quality_profile" not in normalized_generation:
        normalized_generation["quality_profile"] = normalize_string(source.get("quality_profile"), "balanced")

    docs_url = normalize_string(source.get("docs_url") or links.get("docs"))
    timestamp = now_iso()
    created_at = source_metadata.get("created_at") or metadata.get("created_at") or timestamp

    normalized_links = {**links}
    if docs_url:
        normalized_links["docs"] = docs_url

    entry_points = source.get("entry_points") if isinstance(source.get("entry_points"), list) else []
    if not entry_points:
        entry_points = [{"name": "世界线工作台", "type": "route", "route": f"/worldline/{theme_id}"}]
        if db_id:
            entry_points.extend(
                [
                    {"name": "知识库文件", "type": "route", "route": f"/database/{db_id}"},
                    {
                        "name": "知识图谱",
                        "type": "route",
                        "route": f"/graph?db_id={db_id}&knowledge_db_id={db_id}",
                    },
                ]
            )

    return {
        "id": theme_id,
        "name": name,
        "subtitle": normalize_string(source.get("subtitle"), "Live knowledge bridge"),
        "description": normalize_string(source.get("description")),
        "status": normalize_string(source.get("status"), "live"),
        "featured": normalize_bool(source.get("featured"), False),
        "tags": normalize_string_list(source.get("tags")),
        "highlights": normalize_string_list(source.get("highlights")),
        "links": normalized_links,
        "entry_route": f"/themes/{theme_id}",
        "entry_points": entry_points,
        "knowledge": {
            **knowledge,
            "db_id": db_id,
            "knowledge_db_id": db_id,
            "name": knowledge_name,
            "type": knowledge_type,
            "kb_type": knowledge_type,
            "description": knowledge_description,
            "evidence_sources": evidence_sources,
        },
        "context": {
            **context,
            "theme": theme_id,
            "module": theme_id,
            "scene": context.get("scene") or "overview",
            "version": context.get("version") or "worldline-context-v1",
            "db_id": db_id,
            "knowledge_db_id": db_id,
            "knowledge_name": knowledge_name,
            "knowledge_type": knowledge_type,
            "objective": objective,
            "evidence_sources": evidence_sources,
            "generation": normalized_generation,
            "default_question": default_question,
        },
        "worldline": {
            **worldline,
            "db_id": db_id,
            "knowledge_db_id": db_id,
            "objective": objective,
            "evidence_sources": evidence_sources,
            "generation": normalized_generation,
            "default_question": default_question,
            "surfaces": normalize_surface_map(surfaces),
            "capability_map": {
                **capability_map,
                "theme_id": theme_id,
                "db_id": db_id,
                "status": "ready" if db_id else "needs_knowledge_db",
            },
        },
        "metadata": {
            **metadata,
            **source_metadata,
            "source": source_metadata.get("source") or metadata.get("source") or THEME_MODULE_SOURCE,
            "db_id": db_id,
            "knowledge_db_id": db_id,
            "knowledge_name": knowledge_name,
            "knowledge_type": knowledge_type,
            "created_at": created_at,
            "updated_at": timestamp,
        },
    }
