from __future__ import annotations

from importlib import import_module
from typing import Final

from fastapi import APIRouter

RouterSpec = tuple[str, str]

ROUTER_GROUPS: Final[tuple[tuple[str, tuple[RouterSpec, ...]], ...]] = (
    (
        "platform",
        (
            ("server.routers.system_router", "system"),
            ("server.routers.auth_router", "auth"),
            ("server.routers.dashboard_router", "dashboard"),
            ("server.routers.department_router", "department"),
        ),
    ),
    (
        "knowledge",
        (
            ("server.routers.chat_router", "chat"),
            ("server.routers.knowledge_router", "knowledge"),
            ("server.routers.evaluation_router", "evaluation"),
            ("server.routers.mindmap_router", "mindmap"),
            ("server.routers.graph_router", "graph"),
            ("server.routers.task_router", "tasks"),
        ),
    ),
    (
        "operations",
        (
            ("server.routers.mcp_router", "mcp"),
            ("server.routers.skill_router", "skills"),
            ("server.routers.tool_router", "tools"),
            ("server.routers.worldline_run_router", "worldline_runs"),
        ),
    ),
)

_router_cache: APIRouter | None = None


def _load_router(module_name: str, attr_name: str) -> APIRouter:
    module = import_module(module_name)
    router = getattr(module, attr_name)
    if not isinstance(router, APIRouter):
        raise TypeError(f"{module_name}.{attr_name} is not a FastAPI APIRouter")
    return router


def create_api_router() -> APIRouter:
    api_router = APIRouter()

    for _, router_specs in ROUTER_GROUPS:
        for module_name, attr_name in router_specs:
            api_router.include_router(_load_router(module_name, attr_name))

    return api_router


def get_api_router() -> APIRouter:
    global _router_cache
    if _router_cache is None:
        _router_cache = create_api_router()
    return _router_cache


def __getattr__(name: str):
    if name == "router":
        return get_api_router()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["router", "ROUTER_GROUPS", "create_api_router", "get_api_router"]
