from __future__ import annotations

from typing import Any

from src.repositories.knowledge_graph_repository import KnowledgeGraphRepository
from src.utils import hashstr


class WorldlineAgentWorkflowService:
    """Controlled tool manifest and LangGraph-shaped workflow planner."""

    SERVER_NAME = "worldline"
    SERVER_VERSION = "0.1.0"

    TOOL_DEFINITIONS: tuple[dict[str, Any], ...] = (
        {
            "name": "worldline.compile_document",
            "description": "Compile a source document into AST, evidence anchors, and evidence-bound chunks.",
            "write_scope": "knowledge_objects",
            "requires_admin": True,
            "dispatch_backend": "arq",
            "input_schema": {
                "type": "object",
                "required": ["db_id", "file_id"],
                "properties": {
                    "db_id": {"type": "string"},
                    "file_id": {"type": "string"},
                    "parser": {"type": "string"},
                },
            },
        },
        {
            "name": "worldline.rebuild_wiki",
            "description": "Rebuild Auto-Wiki pages through AutoWikiService.",
            "write_scope": "wiki_pages",
            "requires_admin": True,
            "dispatch_backend": "arq",
            "input_schema": {
                "type": "object",
                "required": ["db_id"],
                "properties": {
                    "db_id": {"type": "string"},
                    "file_id": {"type": "string"},
                    "max_topics": {"type": "integer", "minimum": 1, "maximum": 20},
                },
            },
        },
        {
            "name": "worldline.update_graph",
            "description": "Extract evidence-bound graph entities, relationships, and temporal facts.",
            "write_scope": "knowledge_graph",
            "requires_admin": True,
            "dispatch_backend": "arq",
            "input_schema": {
                "type": "object",
                "required": ["db_id"],
                "properties": {
                    "db_id": {"type": "string"},
                    "max_entities": {"type": "integer", "minimum": 1, "maximum": 200},
                },
            },
        },
        {
            "name": "worldline.run_quality_gate",
            "description": "Run the deterministic quality gate and emit failure replay data.",
            "write_scope": "quality_gate_runs",
            "requires_admin": True,
            "dispatch_backend": "arq",
            "input_schema": {
                "type": "object",
                "required": ["db_id"],
                "properties": {
                    "db_id": {"type": "string"},
                    "thresholds": {"type": "object"},
                },
            },
        },
        {
            "name": "worldline.inspect_timeline",
            "description": "Read the evidence-bound timeline for a knowledge base.",
            "write_scope": "none",
            "requires_admin": True,
            "dispatch_backend": "inline",
            "input_schema": {
                "type": "object",
                "required": ["db_id"],
                "properties": {
                    "db_id": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                },
            },
        },
    )

    def __init__(self, repository: KnowledgeGraphRepository | None = None) -> None:
        self.repository = repository or KnowledgeGraphRepository()

    def tool_manifest(self) -> dict[str, Any]:
        return {
            "server": {
                "name": self.SERVER_NAME,
                "version": self.SERVER_VERSION,
                "transport": ["stdio", "streamable_http"],
                "module": "src.mcp.worldline_server",
            },
            "security": {
                "external_agents_direct_db_write": False,
                "all_write_tools_require_admin": True,
                "secrets_in_manifest": False,
            },
            "runtime": {
                "orchestrator": "langgraph",
                "async_dispatch": "arq",
                "controlled_service_boundary": True,
            },
            "tools": list(self.TOOL_DEFINITIONS),
        }

    async def plan_workflow(
        self,
        db_id: str,
        *,
        workflow_type: str = "knowledge_refresh",
        requested_steps: list[str] | None = None,
        created_by: str = "system",
    ) -> dict[str, Any]:
        available = {tool["name"]: tool for tool in self.TOOL_DEFINITIONS}
        default_steps = [
            "worldline.compile_document",
            "worldline.rebuild_wiki",
            "worldline.update_graph",
            "worldline.run_quality_gate",
        ]
        selected = requested_steps or default_steps
        invalid = [step for step in selected if step not in available]
        if invalid:
            raise ValueError(f"Unknown Worldline workflow tools: {', '.join(invalid)}")

        workflow_id = self._workflow_id(db_id, workflow_type, selected)
        nodes = []
        edges = []
        for index, name in enumerate(selected):
            tool = available[name]
            node_id = f"n{index}_{name.rsplit('.', 1)[-1]}"
            nodes.append(
                {
                    "node_id": node_id,
                    "tool": name,
                    "dispatch_backend": tool["dispatch_backend"],
                    "write_scope": tool["write_scope"],
                    "requires_admin": tool["requires_admin"],
                    "arq_task_type": self._arq_task_type(name),
                }
            )
            if index > 0:
                edges.append({"from": nodes[index - 1]["node_id"], "to": node_id, "condition": "success"})

        trace = {
            "orchestrator": "langgraph",
            "dispatch_backend": "arq",
            "edges": edges,
            "policy": "single writer service boundary",
        }
        await self.repository.insert_workflow_run(
            {
                "workflow_id": workflow_id,
                "db_id": db_id,
                "workflow_type": workflow_type,
                "status": "planned",
                "orchestrator": "langgraph",
                "dispatch_backend": "arq",
                "steps": nodes,
                "trace": trace,
                "created_by": created_by,
            }
        )

        return {
            "workflow_id": workflow_id,
            "db_id": db_id,
            "workflow_type": workflow_type,
            "status": "planned",
            "orchestrator": "langgraph",
            "dispatch_backend": "arq",
            "nodes": nodes,
            "edges": edges,
            "tool_count": len(nodes),
        }

    def _workflow_id(self, db_id: str, workflow_type: str, steps: list[str]) -> str:
        step_key = ":/".join(steps)
        return f"wfr_{hashstr(f'{db_id}:{workflow_type}:{step_key}', length=32)}"

    def _arq_task_type(self, tool_name: str) -> str | None:
        if tool_name == "worldline.inspect_timeline":
            return None
        return tool_name.replace("worldline.", "worldline:")
