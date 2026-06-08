import json
import os
import re
import uuid
import aiofiles
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from fastapi import APIRouter, Body, Depends, HTTPException

from src.storage.postgres.models_business import User
from server.utils.auth_middleware import get_admin_user
from src import config
from src.services.theme_module_contract import normalize_theme_payload, safe_theme_id
from src.utils.logging_config import logger

system = APIRouter(prefix="/system", tags=["system"])
_DEPRECATED_ENV_KEYS_WARNED: set[str] = set()
_LEGACY_BRAND_PREFIX = "Y" + "UXI"
_THEME_MODULE_SOURCE = "custom-theme-module"
_WORLDLINE_SURFACE_KEYS = ("wiki", "graph", "timeline", "quality_gate", "mcp", "workflow")


def _legacy_brand_env(suffix: str) -> str:
    return f"{_LEGACY_BRAND_PREFIX}_{suffix}"


def _get_env_with_legacy_fallback(primary_key: str, legacy_key: str, default: str) -> str:
    value = os.environ.get(primary_key)
    if value is not None:
        return value

    legacy_value = os.environ.get(legacy_key)
    if legacy_value is None:
        return default

    if legacy_key not in _DEPRECATED_ENV_KEYS_WARNED:
        message = (
            f"Environment variable '{legacy_key}' is deprecated and will be removed after Phase 8. "
            f"Use '{primary_key}' instead."
        )
        warnings.warn(message, DeprecationWarning, stacklevel=2)
        logger.warning(message)
        _DEPRECATED_ENV_KEYS_WARNED.add(legacy_key)
    return legacy_value


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _theme_modules_path() -> Path:
    return Path(config.save_dir) / "config" / "theme_modules.json"


def _normalize_string(value: Any, default: str = "") -> str:
    if value is None:
        return default
    normalized = str(value).strip()
    return normalized if normalized else default


def _normalize_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    return bool(value)


def _normalize_string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        source = value
    elif isinstance(value, str):
        source = [item.strip() for item in value.split(",")]
    else:
        source = []
    return [str(item).strip() for item in source if str(item).strip()]


def _normalize_surface_map(value: Any) -> dict[str, bool]:
    source = value if isinstance(value, dict) else {}
    result = {key: bool(source.get(key, True)) for key in _WORLDLINE_SURFACE_KEYS}
    for key, item in source.items():
        if key not in result and isinstance(item, bool):
            result[str(key)] = item
    return result


def _safe_theme_id(value: Any) -> str:
    candidate = _normalize_string(value).lower()
    candidate = re.sub(r"[^a-z0-9_-]+", "-", candidate)
    candidate = re.sub(r"-{2,}", "-", candidate).strip("-_")
    return candidate[:80] or f"module-{uuid.uuid4().hex[:8]}"


def _extract_theme_db_id(theme: dict[str, Any]) -> str:
    context = theme.get("context") if isinstance(theme.get("context"), dict) else {}
    worldline = theme.get("worldline") if isinstance(theme.get("worldline"), dict) else {}
    knowledge = theme.get("knowledge") if isinstance(theme.get("knowledge"), dict) else {}
    metadata = theme.get("metadata") if isinstance(theme.get("metadata"), dict) else {}
    return _normalize_string(
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


def _normalize_theme_payload(
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

    theme_id = fixed_id or _safe_theme_id(source.get("id") or source.get("name") or source.get("title"))
    name = _normalize_string(source.get("name") or source.get("title"), "自定义知识模块")
    db_id = _extract_theme_db_id(source)
    knowledge_name = _normalize_string(
        source.get("knowledge_name")
        or source.get("database_name")
        or knowledge.get("name")
        or metadata.get("knowledge_name")
    )
    knowledge_type = _normalize_string(
        source.get("knowledge_type")
        or source.get("kb_type")
        or knowledge.get("type")
        or knowledge.get("kb_type")
        or metadata.get("knowledge_type")
    )
    knowledge_description = _normalize_string(
        source.get("knowledge_description")
        or knowledge.get("description")
        or metadata.get("knowledge_description")
    )
    objective = _normalize_string(
        source.get("objective")
        or worldline.get("objective")
        or context.get("objective")
        or knowledge.get("objective"),
        "围绕绑定知识库生成可验证的世界线。"
    )
    evidence_sources = _normalize_string_list(
        source.get("evidence_sources")
        or worldline.get("evidence_sources")
        or context.get("evidence_sources")
        or knowledge.get("evidence_sources")
    )
    default_question = _normalize_string(
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
    normalized_generation = {
        **context_generation,
        **generation,
        **source_generation,
    }
    if "mode" not in normalized_generation:
        normalized_generation["mode"] = _normalize_string(source.get("generation_mode"), "base")
    if "branch_budget" not in normalized_generation:
        normalized_generation["branch_budget"] = source.get("branch_budget") or 3
    if "quality_profile" not in normalized_generation:
        normalized_generation["quality_profile"] = _normalize_string(source.get("quality_profile"), "balanced")
    docs_url = _normalize_string(source.get("docs_url") or links.get("docs"))
    now = _now_iso()
    created_at = source_metadata.get("created_at") or metadata.get("created_at") or now

    normalized_links = {**links}
    if docs_url:
        normalized_links["docs"] = docs_url

    entry_points = source.get("entry_points") if isinstance(source.get("entry_points"), list) else []
    if not entry_points:
        entry_points = [
            {"name": "世界线工作台", "type": "route", "route": f"/worldline/{theme_id}"},
        ]
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
        "subtitle": _normalize_string(source.get("subtitle"), "Live knowledge bridge"),
        "description": _normalize_string(source.get("description")),
        "status": _normalize_string(source.get("status"), "live"),
        "featured": _normalize_bool(source.get("featured"), False),
        "tags": _normalize_string_list(source.get("tags")),
        "highlights": _normalize_string_list(source.get("highlights")),
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
            "surfaces": _normalize_surface_map(surfaces),
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
            "source": source_metadata.get("source") or metadata.get("source") or _THEME_MODULE_SOURCE,
            "db_id": db_id,
            "knowledge_db_id": db_id,
            "knowledge_name": knowledge_name,
            "knowledge_type": knowledge_type,
            "created_at": created_at,
            "updated_at": now,
        },
    }


async def load_custom_theme_modules() -> list[dict[str, Any]]:
    path = _theme_modules_path()
    if not path.exists():
        return []

    try:
        async with aiofiles.open(path, encoding="utf-8") as file:
            content = await file.read()
        raw_data = json.loads(content or "{}")
        raw_themes = raw_data if isinstance(raw_data, list) else raw_data.get("themes", [])
        if not isinstance(raw_themes, list):
            return []
        return [
            normalize_theme_payload(item, fixed_id=safe_theme_id(item.get("id")))
            for item in raw_themes
            if isinstance(item, dict)
        ]
    except Exception as e:
        logger.error(f"Failed to load custom theme modules: {e}")
        return []


async def save_custom_theme_modules(themes: list[dict[str, Any]]) -> None:
    path = _theme_modules_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"themes": themes}
    async with aiofiles.open(path, "w", encoding="utf-8") as file:
        await file.write(json.dumps(payload, ensure_ascii=False, indent=2))


def _merge_theme_modules(info_config: dict[str, Any], custom_themes: list[dict[str, Any]]) -> dict[str, Any]:
    merged_config = {**(info_config or {})}
    merged_by_id: dict[str, dict[str, Any]] = {}

    for item in merged_config.get("themes") or []:
        if not isinstance(item, dict):
            continue
        theme_id = _normalize_string(item.get("id"))
        if theme_id:
            merged_by_id[theme_id] = item

    for item in custom_themes:
        theme_id = _normalize_string(item.get("id"))
        if theme_id:
            merged_by_id[theme_id] = item

    merged_config["themes"] = list(merged_by_id.values())
    return merged_config

# =============================================================================
# === 健康检查分组 ===
# =============================================================================


@system.get("/health")
async def health_check():
    """系统健康检查接口（公开接口）"""
    return {"status": "ok", "message": "服务正常运行"}


# =============================================================================
# === 配置管理分组 ===
# =============================================================================


@system.get("/config")
async def get_config(current_user: User = Depends(get_admin_user)):
    """获取系统配置"""
    return config.dump_config()


@system.post("/config")
async def update_config_single(key=Body(...), value=Body(...), current_user: User = Depends(get_admin_user)) -> dict:
    """更新单个配置项"""
    config[key] = value
    config.save()
    return config.dump_config()


@system.post("/config/update")
async def update_config_batch(items: dict = Body(...), current_user: User = Depends(get_admin_user)) -> dict:
    """批量更新配置项"""
    config.update(items)
    config.save()
    return config.dump_config()


@system.get("/logs")
async def get_system_logs(levels: str | None = None, current_user: User = Depends(get_admin_user)):
    """获取系统日志

    Args:
        levels: 可选的日志级别过滤，多个级别用逗号分隔，如 "INFO,ERROR,DEBUG,WARNING"
    """
    try:
        from src.utils.logging_config import LOG_FILE

        # 解析日志级别过滤条件
        level_filter = None
        if levels:
            level_filter = set(level.strip().upper() for level in levels.split(",") if level.strip())

        async with aiofiles.open(LOG_FILE) as f:
            # 读取最后1000行
            lines = []
            async for line in f:
                filtered_line = line.rstrip("\n\r")
                # 如果指定了日志级别过滤，则按级别过滤
                if level_filter:
                    # 日志格式: 2025-03-10 08:26:37,269 - INFO - module - message
                    # 提取日志级别
                    parts = filtered_line.split(" - ")
                    if len(parts) >= 2 and parts[1].strip() in level_filter:
                        lines.append(filtered_line + "\n")
                    # 继续读取以保持行数统计准确
                    if len(lines) > 1000:
                        lines.pop(0)
                else:
                    lines.append(filtered_line + "\n")
                    if len(lines) > 1000:
                        lines.pop(0)

        log = "".join(lines)
        return {"log": log, "message": "success", "log_file": LOG_FILE}
    except Exception as e:
        logger.error(f"获取系统日志失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取系统日志失败: {str(e)}")


# =============================================================================
# === 信息管理分组 ===
# =============================================================================


async def load_info_config():
    """加载信息配置文件"""
    try:
        # 配置文件路径
        brand_file_path = _get_env_with_legacy_fallback(
            "WORLDLINE_BRAND_FILE_PATH",
            _legacy_brand_env("BRAND_FILE_PATH"),
            "src/config/static/info.local.yaml",
        )
        config_path = Path(brand_file_path)

        # 检查文件是否存在
        if not config_path.exists():
            logger.debug(f"The config file {config_path} does not exist, using default config")
            config_path = Path("src/config/static/info.template.yaml")

        # 异步读取配置文件
        async with aiofiles.open(config_path, encoding="utf-8") as file:
            content = await file.read()
            config = yaml.safe_load(content)

        custom_themes = await load_custom_theme_modules()
        return _merge_theme_modules(config or {}, custom_themes)

    except Exception as e:
        logger.error(f"Failed to load info config: {e}")
        return {}


@system.get("/info")
async def get_info_config():
    """获取系统信息配置（公开接口，无需认证）"""
    try:
        config = await load_info_config()
        return {"success": True, "data": config}
    except Exception as e:
        logger.error(f"获取信息配置失败: {e}")
        raise HTTPException(status_code=500, detail="获取信息配置失败")


@system.post("/info/reload")
async def reload_info_config(current_user: User = Depends(get_admin_user)):
    """重新加载信息配置"""
    try:
        config = await load_info_config()
        return {"success": True, "message": "配置重新加载成功", "data": config}
    except Exception as e:
        logger.error(f"重新加载信息配置失败: {e}")
        raise HTTPException(status_code=500, detail="重新加载信息配置失败")


@system.get("/themes")
async def list_theme_modules():
    """获取自定义主题模块。"""
    try:
        themes = await load_custom_theme_modules()
        return {"success": True, "themes": themes}
    except Exception as e:
        logger.error(f"获取主题模块失败: {e}")
        raise HTTPException(status_code=500, detail="获取主题模块失败")


@system.post("/themes")
async def create_theme_module(payload: dict = Body(...), current_user: User = Depends(get_admin_user)):
    """创建自定义主题模块。"""
    try:
        themes = await load_custom_theme_modules()
        theme = normalize_theme_payload(payload)
        if any(item.get("id") == theme["id"] for item in themes):
            raise HTTPException(status_code=409, detail=f"主题模块 '{theme['id']}' 已存在")
        themes.append(theme)
        await save_custom_theme_modules(themes)
        return {"success": True, "theme": theme, "themes": themes}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建主题模块失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建主题模块失败: {e}")


@system.put("/themes/{theme_id}")
async def update_theme_module(
    theme_id: str,
    payload: dict = Body(...),
    current_user: User = Depends(get_admin_user),
):
    """更新自定义主题模块。"""
    try:
        normalized_id = safe_theme_id(theme_id)
        themes = await load_custom_theme_modules()
        for index, item in enumerate(themes):
            if item.get("id") == normalized_id:
                updated = normalize_theme_payload(payload, existing=item, fixed_id=normalized_id)
                themes[index] = updated
                await save_custom_theme_modules(themes)
                return {"success": True, "theme": updated, "themes": themes}
        raise HTTPException(status_code=404, detail=f"主题模块 '{normalized_id}' 不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新主题模块失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新主题模块失败: {e}")


@system.delete("/themes/{theme_id}")
async def delete_theme_module(theme_id: str, current_user: User = Depends(get_admin_user)):
    """删除自定义主题模块。"""
    try:
        normalized_id = safe_theme_id(theme_id)
        themes = await load_custom_theme_modules()
        kept_themes = [item for item in themes if item.get("id") != normalized_id]
        if len(kept_themes) == len(themes):
            raise HTTPException(status_code=404, detail=f"主题模块 '{normalized_id}' 不存在")
        await save_custom_theme_modules(kept_themes)
        return {"success": True, "themes": kept_themes}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除主题模块失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除主题模块失败: {e}")


# =============================================================================
# === OCR服务分组 ===
# =============================================================================


@system.get("/ocr/health")
async def check_ocr_services_health(current_user: User = Depends(get_admin_user)):
    """
    检查所有OCR服务的健康状态
    返回各个OCR服务的可用性信息
    """
    from src.plugins.document_processor_factory import DocumentProcessorFactory

    try:
        # 使用统一的健康检查接口
        health_status = DocumentProcessorFactory.check_all_health()

        # 转换为旧格式以保持API兼容性
        formatted_status = {}
        for service_name, health_info in health_status.items():
            formatted_status[service_name] = {
                "status": health_info.get("status", "unknown"),
                "message": health_info.get("message", ""),
                "details": health_info.get("details", {}),
            }

        # 计算整体健康状态
        overall_status = (
            "healthy" if any(svc["status"] == "healthy" for svc in formatted_status.values()) else "unhealthy"
        )

        return {
            "overall_status": overall_status,
            "services": formatted_status,
            "message": "OCR服务健康检查完成",
        }

    except Exception as e:
        logger.error(f"OCR健康检查失败: {str(e)}")
        return {
            "overall_status": "error",
            "services": {},
            "message": f"OCR健康检查失败: {str(e)}",
        }


# =============================================================================
# === 聊天模型状态检查分组 ===
# =============================================================================


@system.get("/chat-models/status")
async def get_chat_model_status(provider: str, model_name: str, current_user: User = Depends(get_admin_user)):
    """获取指定聊天模型的状态"""
    logger.debug(f"Checking chat model status: {provider}/{model_name}")
    try:
        from src.models.chat import test_chat_model_status

        status = await test_chat_model_status(provider, model_name)
        return {"status": status, "message": "success"}
    except Exception as e:
        logger.error(f"获取聊天模型状态失败 {provider}/{model_name}: {e}")
        return {
            "message": f"获取聊天模型状态失败: {e}",
            "status": {"provider": provider, "model_name": model_name, "status": "error", "message": str(e)},
        }


@system.get("/chat-models/all/status")
async def get_all_chat_models_status(current_user: User = Depends(get_admin_user)):
    """获取所有聊天模型的状态"""
    logger.debug("Checking all chat models status")
    try:
        from src.models.chat import test_all_chat_models_status

        status = await test_all_chat_models_status()
        return {"status": status, "message": "success"}
    except Exception as e:
        logger.error(f"获取所有聊天模型状态失败: {e}")
        return {"message": f"获取所有聊天模型状态失败: {e}", "status": {"models": {}, "total": 0, "available": 0}}


# =============================================================================
# === 自定义供应商管理分组 ===
# =============================================================================


@system.get("/custom-providers")
async def get_custom_providers(current_user: User = Depends(get_admin_user)):
    """获取所有自定义供应商"""
    try:
        custom_providers = config.get_custom_providers()
        return {
            "providers": {provider: info.model_dump() for provider, info in custom_providers.items()},
            "message": "success",
        }
    except Exception as e:
        logger.error(f"获取自定义供应商失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取自定义供应商失败: {str(e)}")


@system.post("/custom-providers")
async def add_custom_provider(
    provider_id: str = Body(..., description="供应商ID"),
    provider_data: dict = Body(..., description="供应商配置数据"),
    current_user: User = Depends(get_admin_user),
):
    """添加自定义供应商"""
    try:
        success = config.add_custom_provider(provider_id, provider_data)
        if success:
            return {"message": f"自定义供应商 {provider_id} 添加成功"}
        else:
            raise HTTPException(status_code=400, detail=f"供应商ID {provider_id} 已存在，请使用其他ID")
    except Exception as e:
        logger.error(f"添加自定义供应商失败 {provider_id}: {e}")
        raise HTTPException(status_code=500, detail=f"添加自定义供应商失败: {str(e)}")


@system.put("/custom-providers/{provider_id}")
async def update_custom_provider(
    provider_id: str,
    provider_data: dict = Body(..., description="供应商配置数据"),
    current_user: User = Depends(get_admin_user),
):
    """更新自定义供应商"""
    try:
        success = config.update_custom_provider(provider_id, provider_data)
        if success:
            return {"message": f"自定义供应商 {provider_id} 更新成功"}
        else:
            raise HTTPException(status_code=404, detail=f"自定义供应商 {provider_id} 不存在或更新失败")
    except Exception as e:
        logger.error(f"更新自定义供应商失败 {provider_id}: {e}")
        raise HTTPException(status_code=500, detail=f"更新自定义供应商失败: {str(e)}")


@system.delete("/custom-providers/{provider_id}")
async def delete_custom_provider(provider_id: str, current_user: User = Depends(get_admin_user)):
    """删除自定义供应商"""
    try:
        success = config.delete_custom_provider(provider_id)
        if success:
            return {"message": f"自定义供应商 {provider_id} 删除成功"}
        else:
            raise HTTPException(status_code=404, detail=f"自定义供应商 {provider_id} 不存在或删除失败")
    except Exception as e:
        logger.error(f"删除自定义供应商失败 {provider_id}: {e}")
        raise HTTPException(status_code=500, detail=f"删除自定义供应商失败: {str(e)}")


@system.post("/custom-providers/{provider_id}/test")
async def test_custom_provider(
    provider_id: str, request: dict = Body(..., description="测试请求"), current_user: User = Depends(get_admin_user)
):
    """测试自定义供应商连接"""
    try:
        # 从请求中获取model_name
        model_name = request.get("model_name")
        if not model_name:
            raise HTTPException(status_code=400, detail="缺少model_name参数")

        # 检查供应商是否存在
        if provider_id not in config.model_names:
            raise HTTPException(status_code=404, detail=f"供应商 {provider_id} 不存在")

        # 测试模型状态
        from src.models.chat import test_chat_model_status

        status = await test_chat_model_status(provider_id, model_name)
        return {"status": status, "message": "测试完成"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"测试自定义供应商失败 {provider_id}/{model_name}: {e}")
        return {
            "message": f"测试自定义供应商失败: {e}",
            "status": {"provider": provider_id, "model_name": model_name, "status": "error", "message": str(e)},
        }
