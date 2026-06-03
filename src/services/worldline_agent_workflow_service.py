from __future__ import annotations

from typing import Any

from src.repositories.knowledge_graph_repository import KnowledgeGraphRepository
from src.utils import hashstr
from src.utils.datetime_utils import utc_now_naive


class WorldlineAgentWorkflowService:
    """Controlled tool manifest and LangGraph-shaped workflow planner."""

    SERVER_NAME = "worldline"
    SERVER_VERSION = "0.2.0"
    SUBAGENT_LANES: tuple[dict[str, Any], ...] = (
        {
            "lane": "research_reviewer",
            "purpose": "Research, compare options, and review evidence without writing project data.",
            "write_scope": "none",
            "allowed_tools": ["GitHub", "Browser/Playwright"],
            "requires_handoff": True,
        },
        {
            "lane": "knowledge_operator",
            "purpose": "Trigger controlled wiki, graph, timeline, and quality-gate workflows.",
            "write_scope": "worldline_service_boundary",
            "allowed_tools": ["worldline"],
            "requires_admin": True,
            "requires_handoff": True,
        },
        {
            "lane": "frontend_qa",
            "purpose": "Run local browser screenshot QA for Worldline workbench pages.",
            "write_scope": "artifacts_only",
            "allowed_tools": ["Browser/Playwright"],
            "allowed_targets": ["localhost", "127.0.0.1"],
            "requires_handoff": False,
        },
        {
            "lane": "release_auditor",
            "purpose": "Run deterministic release gates and record validation evidence.",
            "write_scope": "task_evidence",
            "allowed_tools": ["worldline_release_gate", "pytest", "vite", "docker compose config"],
            "requires_handoff": False,
        },
    )

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
            "audit": {
                "enabled": True,
                "table": "worldline_mcp_audit_logs",
                "records_tool_name_actor_status_and_summaries": True,
            },
            "subagents": {
                "single_writer_policy": True,
                "parallel_writes_to_same_files": False,
                "lanes": list(self.SUBAGENT_LANES),
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
            "subagent_policy": {
                "single_writer": True,
                "handoff_required_for_write_lanes": True,
            },
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
        await self.audit_tool_call(
            db_id,
            tool_name="worldline.plan_workflow",
            actor=created_by,
            status="success",
            request_summary={"workflow_type": workflow_type, "requested_steps": selected},
            result_summary={"workflow_id": workflow_id, "tool_count": len(nodes)},
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

    async def audit_tool_call(
        self,
        db_id: str,
        *,
        tool_name: str,
        actor: str | None = None,
        status: str = "success",
        request_summary: dict[str, Any] | None = None,
        result_summary: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        log_id = self._audit_log_id(db_id, tool_name, request_summary or {}, result_summary or {})
        log = await self.repository.insert_mcp_audit_log(
            {
                "log_id": log_id,
                "db_id": db_id,
                "tool_name": tool_name,
                "actor": actor,
                "status": status,
                "request_summary": request_summary or {},
                "result_summary": result_summary or {},
                "audit_metadata": metadata or {"source": "WorldlineAgentWorkflowService"},
                "started_at": utc_now_naive(),
                "completed_at": utc_now_naive(),
            }
        )
        return self.repository.serialize_mcp_audit_log(log)

    async def list_audit_logs(
        self,
        db_id: str,
        *,
        tool_name: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        return await self.repository.list_mcp_audit_logs(db_id, tool_name=tool_name, limit=limit, offset=offset)

    def _workflow_id(self, db_id: str, workflow_type: str, steps: list[str]) -> str:
        step_key = ":/".join(steps)
        return f"wfr_{hashstr(f'{db_id}:{workflow_type}:{step_key}', length=32)}"

    def _arq_task_type(self, tool_name: str) -> str | None:
        if tool_name == "worldline.inspect_timeline":
            return None
        return tool_name.replace("worldline.", "worldline:")

    def _audit_log_id(
        self,
        db_id: str,
        tool_name: str,
        request_summary: dict[str, Any],
        result_summary: dict[str, Any],
    ) -> str:
        payload = f"{db_id}:{tool_name}:{request_summary}:{result_summary}:{utc_now_naive().isoformat()}"
        return f"wl_audit_{hashstr(payload, length=32)}"
