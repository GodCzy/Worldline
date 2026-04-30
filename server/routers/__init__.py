from collections.abc import Iterable

from fastapi import APIRouter

from server.routers.auth_router import auth
from server.routers.chat_router import chat
from server.routers.dashboard_router import dashboard
from server.routers.department_router import department
from server.routers.evaluation_router import evaluation
from server.routers.graph_router import graph
from server.routers.knowledge_router import knowledge
from server.routers.mcp_router import mcp
from server.routers.mindmap_router import mindmap
from server.routers.skill_router import skills
from server.routers.system_router import system
from server.routers.task_router import tasks
from server.routers.tool_router import tools

PLATFORM_ROUTERS = (
    system,
    auth,
    dashboard,
    department,
)

KNOWLEDGE_ROUTERS = (
    chat,
    knowledge,
    evaluation,
    mindmap,
    graph,
    tasks,
)

OPERATIONS_ROUTERS = (
    mcp,
    skills,
    tools,
)

ROUTER_GROUPS: tuple[tuple[str, Iterable[APIRouter]], ...] = (
    ("platform", PLATFORM_ROUTERS),
    ("knowledge", KNOWLEDGE_ROUTERS),
    ("operations", OPERATIONS_ROUTERS),
)


def create_api_router() -> APIRouter:
    api_router = APIRouter()

    for _, routers in ROUTER_GROUPS:
        for child_router in routers:
            api_router.include_router(child_router)

    return api_router


router = create_api_router()

__all__ = ["router", "ROUTER_GROUPS", "create_api_router"]
