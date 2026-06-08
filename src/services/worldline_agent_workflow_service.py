from __future__ import annotations

from typing import Any

from src.repositories.knowledge_graph_repository import KnowledgeGraphRepository
from src.services.worldline_run_ledger_service import WorldlineRunLedgerService
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
        {
            "name": "worldline.inspect_run_artifacts",
            "description": "Read saved Agent run replay artifacts from the controlled run ledger.",
            "write_scope": "none",
            "requires_admin": True,
            "dispatch_backend": "inline",
            "input_schema": {
                "type": "object",
                "required": ["run_id"],
                "properties": {
                    "run_id": {"type": "string"},
                    "artifact_id": {"type": "string"},
                    "include_content": {"type": "boolean", "default": False},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                    "audit_db_id": {
                        "type": "string",
                        "description": "Optional knowledge db id used only for MCP audit logging.",
                    },
                },
            },
        },
        {
            "name": "worldline.inspect_run_gates",
            "description": "Read Agent run quality-gate results from the controlled run ledger.",
            "write_scope": "none",
            "requires_admin": True,
            "dispatch_backend": "inline",
            "input_schema": {
                "type": "object",
                "required": ["run_id"],
                "properties": {
                    "run_id": {"type": "string"},
                    "gate_id": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                    "audit_db_id": {
                        "type": "string",
                        "description": "Optional knowledge db id used only for MCP audit logging.",
                    },
                },
            },
        },
        {
            "name": "worldline.inspect_run_evidence",
            "description": "Read Agent run EvidenceAnchor and SourceAsset metadata from the controlled run ledger.",
            "write_scope": "none",
            "requires_admin": True,
            "dispatch_backend": "inline",
            "input_schema": {
                "type": "object",
                "required": ["run_id"],
                "properties": {
                    "run_id": {"type": "string"},
                    "evidence_id": {"type": "string"},
                    "source_id": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                    "audit_db_id": {
                        "type": "string",
                        "description": "Optional knowledge db id used only for MCP audit logging.",
                    },
                },
            },
        },
        {
            "name": "worldline.inspect_run_knowledge",
            "description": "Read Agent run WikiPage, KnowledgeEntity, and TemporalFact metadata from the controlled run ledger.",
            "write_scope": "none",
            "requires_admin": True,
            "dispatch_backend": "inline",
            "input_schema": {
                "type": "object",
                "required": ["run_id"],
                "properties": {
                    "run_id": {"type": "string"},
                    "kind": {
                        "type": "string",
                        "enum": ["all", "wiki", "graph", "timeline"],
                        "default": "all",
                    },
                    "item_id": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                    "audit_db_id": {
                        "type": "string",
                        "description": "Optional knowledge db id used only for MCP audit logging.",
                    },
                },
            },
        },
        {
            "name": "worldline.inspect_run_manifest",
            "description": "Read a run-scoped manifest of all controlled Agent read resources and MCP call args.",
            "write_scope": "none",
            "requires_admin": True,
            "dispatch_backend": "inline",
            "input_schema": {
                "type": "object",
                "required": ["run_id"],
                "properties": {
                    "run_id": {"type": "string"},
                    "include_resources": {"type": "boolean", "default": True},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                    "audit_db_id": {
                        "type": "string",
                        "description": "Optional knowledge db id used only for MCP audit logging.",
                    },
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

    async def inspect_run_artifacts(
        self,
        run_id: str,
        *,
        artifact_id: str | None = None,
        include_content: bool = False,
        limit: int = 20,
        audit_db_id: str | None = None,
        actor: str = "mcp",
    ) -> dict[str, Any]:
        normalized_limit = max(1, min(int(limit or 20), 100))
        query_limit = 500 if artifact_id else normalized_limit
        artifacts = await WorldlineRunLedgerService().list_artifacts(run_id, limit=query_limit)

        if artifacts is None:
            result: dict[str, Any] = {
                "status": "not_found",
                "run_id": run_id,
                "artifact_id": artifact_id or "",
                "items": [],
                "total": 0,
                "content_included": include_content,
                "storage": {"type": "worldline_run_ledger", "read_only": True},
            }
        else:
            items = [_as_artifact_view(item, include_content=include_content) for item in artifacts.get("items", [])]
            selected = None
            if artifact_id:
                selected = next((item for item in items if item.get("id") == artifact_id), None)
                items = [selected] if selected else []
            result = {
                "status": "ok" if not artifact_id or selected else "not_found",
                "run_id": run_id,
                "artifact_id": artifact_id or "",
                "items": items,
                "selected": selected,
                "total": artifacts.get("total", len(items)),
                "limit": artifacts.get("limit", normalized_limit),
                "offset": artifacts.get("offset", 0),
                "content_included": include_content,
                "storage": {"type": "worldline_run_ledger", "read_only": True},
            }

        result["audit"] = await self._audit_run_artifact_inspection(
            audit_db_id=audit_db_id,
            actor=actor,
            run_id=run_id,
            artifact_id=artifact_id or "",
            include_content=include_content,
            result=result,
        )
        return result

    async def inspect_run_gates(
        self,
        run_id: str,
        *,
        gate_id: str | None = None,
        limit: int = 20,
        audit_db_id: str | None = None,
        actor: str = "mcp",
    ) -> dict[str, Any]:
        normalized_limit = max(1, min(int(limit or 20), 100))
        query_limit = 500 if gate_id else normalized_limit
        gates = await WorldlineRunLedgerService().list_gates(run_id, limit=query_limit)

        if gates is None:
            result: dict[str, Any] = {
                "status": "not_found",
                "run_id": run_id,
                "gate_id": gate_id or "",
                "items": [],
                "total": 0,
                "storage": {"type": "worldline_run_ledger", "read_only": True},
            }
        else:
            items = [_as_gate_view(item, run_id=run_id) for item in gates.get("items", [])]
            selected = None
            if gate_id:
                selected = next((item for item in items if item.get("id") == gate_id), None)
                items = [selected] if selected else []
            result = {
                "status": "ok" if not gate_id or selected else "not_found",
                "run_id": run_id,
                "gate_id": gate_id or "",
                "items": items,
                "selected": selected,
                "total": gates.get("total", len(items)),
                "limit": gates.get("limit", normalized_limit),
                "offset": gates.get("offset", 0),
                "storage": {"type": "worldline_run_ledger", "read_only": True},
            }

        result["audit"] = await self._audit_run_gate_inspection(
            audit_db_id=audit_db_id,
            actor=actor,
            run_id=run_id,
            gate_id=gate_id or "",
            result=result,
        )
        return result

    async def inspect_run_evidence(
        self,
        run_id: str,
        *,
        evidence_id: str | None = None,
        source_id: str | None = None,
        limit: int = 20,
        audit_db_id: str | None = None,
        actor: str = "mcp",
    ) -> dict[str, Any]:
        normalized_limit = max(1, min(int(limit or 20), 100))
        query_limit = 500 if evidence_id or source_id else normalized_limit
        evidence = await WorldlineRunLedgerService().list_evidence(run_id, limit=query_limit)

        if evidence is None:
            result: dict[str, Any] = {
                "status": "not_found",
                "run_id": run_id,
                "evidence_id": evidence_id or "",
                "source_id": source_id or "",
                "items": [],
                "total": 0,
                "storage": {"type": "worldline_run_ledger", "read_only": True},
            }
        else:
            items = [_as_evidence_view(item, run_id=run_id) for item in evidence.get("items", [])]
            selected = None
            if evidence_id:
                selected = next((item for item in items if item.get("id") == evidence_id or item.get("evidenceId") == evidence_id), None)
                items = [selected] if selected else []
            elif source_id:
                selected = next((item for item in items if _evidence_source_id(item) == source_id), None)
                items = [selected] if selected else []
            result = {
                "status": "ok" if not (evidence_id or source_id) or selected else "not_found",
                "run_id": run_id,
                "evidence_id": evidence_id or "",
                "source_id": source_id or "",
                "items": items,
                "selected": selected,
                "total": evidence.get("total", len(items)),
                "limit": evidence.get("limit", normalized_limit),
                "offset": evidence.get("offset", 0),
                "storage": {"type": "worldline_run_ledger", "read_only": True},
            }

        result["audit"] = await self._audit_run_evidence_inspection(
            audit_db_id=audit_db_id,
            actor=actor,
            run_id=run_id,
            evidence_id=evidence_id or "",
            source_id=source_id or "",
            result=result,
        )
        return result

    async def inspect_run_knowledge(
        self,
        run_id: str,
        *,
        kind: str = "all",
        item_id: str | None = None,
        limit: int = 20,
        audit_db_id: str | None = None,
        actor: str = "mcp",
    ) -> dict[str, Any]:
        normalized_kind = str(kind or "all").strip().lower()
        if normalized_kind not in {"all", "wiki", "graph", "timeline"}:
            normalized_kind = "all"
        normalized_limit = max(1, min(int(limit or 20), 100))
        query_limit = 500 if item_id else normalized_limit
        knowledge = await WorldlineRunLedgerService().list_knowledge(run_id, kind=normalized_kind, limit=query_limit)

        if knowledge is None:
            result: dict[str, Any] = {
                "status": "not_found",
                "run_id": run_id,
                "kind": normalized_kind,
                "item_id": item_id or "",
                "items": [],
                "total": 0,
                "storage": {"type": "worldline_run_ledger", "read_only": True},
            }
        else:
            items = [_as_knowledge_view(item, run_id=run_id) for item in knowledge.get("items", [])]
            selected = None
            if item_id:
                selected = next((item for item in items if _knowledge_item_matches(item, item_id)), None)
                items = [selected] if selected else []
            result = {
                "status": "ok" if not item_id or selected else "not_found",
                "run_id": run_id,
                "kind": normalized_kind,
                "item_id": item_id or "",
                "items": items,
                "selected": selected,
                "total": knowledge.get("total", len(items)),
                "limit": knowledge.get("limit", normalized_limit),
                "offset": knowledge.get("offset", 0),
                "storage": {"type": "worldline_run_ledger", "read_only": True},
            }

        result["audit"] = await self._audit_run_knowledge_inspection(
            audit_db_id=audit_db_id,
            actor=actor,
            run_id=run_id,
            kind=normalized_kind,
            item_id=item_id or "",
            result=result,
        )
        return result

    async def inspect_run_manifest(
        self,
        run_id: str,
        *,
        include_resources: bool = True,
        limit: int = 50,
        audit_db_id: str | None = None,
        actor: str = "mcp",
    ) -> dict[str, Any]:
        normalized_limit = max(1, min(int(limit or 50), 100))
        ledger = WorldlineRunLedgerService()
        run = await ledger.get_run(run_id)

        if run is None:
            result: dict[str, Any] = {
                "status": "not_found",
                "contractVersion": "worldline-run-mcp-manifest-v0.1",
                "run_id": run_id,
                "sections": {},
                "resourceCounts": {},
                "tools": [],
                "storage": {"type": "worldline_run_ledger", "read_only": True},
            }
        else:
            artifacts = await ledger.list_artifacts(run_id, limit=normalized_limit)
            gates = await ledger.list_gates(run_id, limit=normalized_limit)
            evidence = await ledger.list_evidence(run_id, limit=normalized_limit)
            knowledge = await ledger.list_knowledge(run_id, kind="all", limit=normalized_limit)

            artifact_views = [_as_artifact_view(item, include_content=False) for item in (artifacts or {}).get("items", [])]
            gate_views = [_as_gate_view(item, run_id=run_id) for item in (gates or {}).get("items", [])]
            evidence_views = [_as_evidence_view(item, run_id=run_id) for item in (evidence or {}).get("items", [])]
            source_views = _source_manifest_views(evidence_views, run_id=run_id)
            knowledge_views = [_as_knowledge_view(item, run_id=run_id) for item in (knowledge or {}).get("items", [])]
            wiki_views = [item for item in knowledge_views if item.get("kind") == "wiki"]
            graph_views = [item for item in knowledge_views if item.get("kind") == "graph"]
            timeline_views = [item for item in knowledge_views if item.get("kind") == "timeline"]

            sections = {
                "artifacts": _manifest_section(
                    run_id,
                    section_id="artifacts",
                    label="Replay Artifacts",
                    tool_name="worldline.inspect_run_artifacts",
                    uri_segment="artifacts",
                    resources=[
                        _manifest_resource(
                            item,
                            tool_name="worldline.inspect_run_artifacts",
                            args={
                                "run_id": run_id,
                                "artifact_id": item.get("id") or "artifact",
                                "include_content": False,
                                "audit_db_id": "",
                            },
                        )
                        for item in artifact_views
                    ],
                    include_resources=include_resources,
                ),
                "gates": _manifest_section(
                    run_id,
                    section_id="gates",
                    label="Quality Gates",
                    tool_name="worldline.inspect_run_gates",
                    uri_segment="gates",
                    resources=[
                        _manifest_resource(
                            item,
                            tool_name="worldline.inspect_run_gates",
                            args={"run_id": run_id, "gate_id": item.get("id") or "gate", "audit_db_id": ""},
                        )
                        for item in gate_views
                    ],
                    include_resources=include_resources,
                ),
                "evidence": _manifest_section(
                    run_id,
                    section_id="evidence",
                    label="Evidence Anchors",
                    tool_name="worldline.inspect_run_evidence",
                    uri_segment="evidence",
                    resources=[
                        _manifest_resource(
                            item,
                            tool_name="worldline.inspect_run_evidence",
                            args={"run_id": run_id, "evidence_id": item.get("evidenceId") or item.get("id") or "evidence", "audit_db_id": ""},
                        )
                        for item in evidence_views
                    ],
                    include_resources=include_resources,
                ),
                "sources": _manifest_section(
                    run_id,
                    section_id="sources",
                    label="Source Assets",
                    tool_name="worldline.inspect_run_evidence",
                    uri_segment="sources",
                    resources=[
                        _manifest_resource(
                            item,
                            tool_name="worldline.inspect_run_evidence",
                            args={"run_id": run_id, "source_id": item.get("id") or "source", "audit_db_id": ""},
                        )
                        for item in source_views
                    ],
                    include_resources=include_resources,
                ),
                "wiki": _manifest_knowledge_section(run_id, "wiki", "Wiki Pages", wiki_views, include_resources=include_resources),
                "graph": _manifest_knowledge_section(run_id, "graph", "Knowledge Entities", graph_views, include_resources=include_resources),
                "timeline": _manifest_knowledge_section(run_id, "timeline", "Temporal Facts", timeline_views, include_resources=include_resources),
            }
            result = {
                "status": "ok",
                "contractVersion": "worldline-run-mcp-manifest-v0.1",
                "run_id": run_id,
                "run": {
                    "id": run.get("id"),
                    "title": run.get("title") or run_id,
                    "status": run.get("status") or "",
                    "activeBranchId": run.get("activeBranchId") or "",
                    "protocolVersion": run.get("protocolVersion") or "",
                    "uri": f"worldline-run-ledger://{run_id}",
                },
                "sections": sections,
                "resourceCounts": {key: value.get("count", 0) for key, value in sections.items()},
                "tools": _run_manifest_tools(),
                "include_resources": include_resources,
                "limit": normalized_limit,
                "storage": {"type": "worldline_run_ledger", "read_only": True},
            }

        result["audit"] = await self._audit_run_manifest_inspection(
            audit_db_id=audit_db_id,
            actor=actor,
            run_id=run_id,
            result=result,
        )
        return result

    async def _audit_run_artifact_inspection(
        self,
        *,
        audit_db_id: str | None,
        actor: str,
        run_id: str,
        artifact_id: str,
        include_content: bool,
        result: dict[str, Any],
    ) -> dict[str, Any]:
        if not audit_db_id:
            return {"recorded": False, "reason": "audit_db_id_not_provided"}
        try:
            log = await self.audit_tool_call(
                audit_db_id,
                tool_name="worldline.inspect_run_artifacts",
                actor=actor,
                status="success" if result.get("status") == "ok" else "not_found",
                request_summary={
                    "run_id": run_id,
                    "artifact_id": artifact_id,
                    "include_content": include_content,
                },
                result_summary={
                    "status": result.get("status"),
                    "item_count": len(result.get("items") or []),
                    "total": result.get("total", 0),
                },
                metadata={"source": "WorldlineAgentWorkflowService", "storage": "worldline_run_ledger"},
            )
            return {"recorded": True, "db_id": audit_db_id, "log_id": log.get("log_id")}
        except Exception as exc:  # noqa: BLE001
            return {"recorded": False, "reason": str(exc), "db_id": audit_db_id}

    async def _audit_run_gate_inspection(
        self,
        *,
        audit_db_id: str | None,
        actor: str,
        run_id: str,
        gate_id: str,
        result: dict[str, Any],
    ) -> dict[str, Any]:
        if not audit_db_id:
            return {"recorded": False, "reason": "audit_db_id_not_provided"}
        try:
            log = await self.audit_tool_call(
                audit_db_id,
                tool_name="worldline.inspect_run_gates",
                actor=actor,
                status="success" if result.get("status") == "ok" else "not_found",
                request_summary={
                    "run_id": run_id,
                    "gate_id": gate_id,
                },
                result_summary={
                    "status": result.get("status"),
                    "item_count": len(result.get("items") or []),
                    "total": result.get("total", 0),
                },
                metadata={"source": "WorldlineAgentWorkflowService", "storage": "worldline_run_ledger"},
            )
            return {"recorded": True, "db_id": audit_db_id, "log_id": log.get("log_id")}
        except Exception as exc:  # noqa: BLE001
            return {"recorded": False, "reason": str(exc), "db_id": audit_db_id}

    async def _audit_run_evidence_inspection(
        self,
        *,
        audit_db_id: str | None,
        actor: str,
        run_id: str,
        evidence_id: str,
        source_id: str,
        result: dict[str, Any],
    ) -> dict[str, Any]:
        if not audit_db_id:
            return {"recorded": False, "reason": "audit_db_id_not_provided"}
        try:
            log = await self.audit_tool_call(
                audit_db_id,
                tool_name="worldline.inspect_run_evidence",
                actor=actor,
                status="success" if result.get("status") == "ok" else "not_found",
                request_summary={
                    "run_id": run_id,
                    "evidence_id": evidence_id,
                    "source_id": source_id,
                },
                result_summary={
                    "status": result.get("status"),
                    "item_count": len(result.get("items") or []),
                    "total": result.get("total", 0),
                },
                metadata={"source": "WorldlineAgentWorkflowService", "storage": "worldline_run_ledger"},
            )
            return {"recorded": True, "db_id": audit_db_id, "log_id": log.get("log_id")}
        except Exception as exc:  # noqa: BLE001
            return {"recorded": False, "reason": str(exc), "db_id": audit_db_id}

    async def _audit_run_knowledge_inspection(
        self,
        *,
        audit_db_id: str | None,
        actor: str,
        run_id: str,
        kind: str,
        item_id: str,
        result: dict[str, Any],
    ) -> dict[str, Any]:
        if not audit_db_id:
            return {"recorded": False, "reason": "audit_db_id_not_provided"}
        try:
            log = await self.audit_tool_call(
                audit_db_id,
                tool_name="worldline.inspect_run_knowledge",
                actor=actor,
                status="success" if result.get("status") == "ok" else "not_found",
                request_summary={
                    "run_id": run_id,
                    "kind": kind,
                    "item_id": item_id,
                },
                result_summary={
                    "status": result.get("status"),
                    "item_count": len(result.get("items") or []),
                    "total": result.get("total", 0),
                },
                metadata={"source": "WorldlineAgentWorkflowService", "storage": "worldline_run_ledger"},
            )
            return {"recorded": True, "db_id": audit_db_id, "log_id": log.get("log_id")}
        except Exception as exc:  # noqa: BLE001
            return {"recorded": False, "reason": str(exc), "db_id": audit_db_id}

    async def _audit_run_manifest_inspection(
        self,
        *,
        audit_db_id: str | None,
        actor: str,
        run_id: str,
        result: dict[str, Any],
    ) -> dict[str, Any]:
        if not audit_db_id:
            return {"recorded": False, "reason": "audit_db_id_not_provided"}
        try:
            log = await self.audit_tool_call(
                audit_db_id,
                tool_name="worldline.inspect_run_manifest",
                actor=actor,
                status="success" if result.get("status") == "ok" else "not_found",
                request_summary={"run_id": run_id},
                result_summary={
                    "status": result.get("status"),
                    "section_count": len(result.get("sections") or {}),
                    "resource_counts": result.get("resourceCounts") or {},
                },
                metadata={"source": "WorldlineAgentWorkflowService", "storage": "worldline_run_ledger"},
            )
            return {"recorded": True, "db_id": audit_db_id, "log_id": log.get("log_id")}
        except Exception as exc:  # noqa: BLE001
            return {"recorded": False, "reason": str(exc), "db_id": audit_db_id}

    def _workflow_id(self, db_id: str, workflow_type: str, steps: list[str]) -> str:
        step_key = ":/".join(steps)
        return f"wfr_{hashstr(f'{db_id}:{workflow_type}:{step_key}', length=32)}"

    def _arq_task_type(self, tool_name: str) -> str | None:
        if tool_name in {
            "worldline.inspect_timeline",
            "worldline.inspect_run_artifacts",
            "worldline.inspect_run_gates",
            "worldline.inspect_run_evidence",
            "worldline.inspect_run_knowledge",
            "worldline.inspect_run_manifest",
        }:
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


def _as_artifact_view(artifact: dict[str, Any], *, include_content: bool) -> dict[str, Any]:
    content = artifact.get("content") if include_content else None
    markdown = artifact.get("markdown") if include_content else None
    markdown_preview = str(artifact.get("markdown") or "")[:480]
    content_summary = _artifact_content_summary(artifact.get("content"))
    view = {
        "id": artifact.get("id"),
        "runId": artifact.get("runId"),
        "eventId": artifact.get("eventId") or "",
        "branchId": artifact.get("branchId") or "",
        "kind": artifact.get("kind") or "artifact",
        "format": artifact.get("format") or "",
        "label": artifact.get("label") or artifact.get("id"),
        "summary": artifact.get("summary") or "",
        "uri": f"worldline-run-ledger://{artifact.get('runId')}/artifacts/{artifact.get('id')}",
        "size": artifact.get("size") or 0,
        "createdBy": artifact.get("createdBy") or "",
        "createdAt": artifact.get("createdAt") or "",
        "updatedAt": artifact.get("updatedAt") or "",
        "has_content": artifact.get("content") is not None,
        "has_markdown": bool(artifact.get("markdown")),
        "markdown_preview": markdown_preview,
        "content_summary": content_summary,
    }
    if include_content:
        view["content"] = content
        view["markdown"] = markdown
    return view


def _as_gate_view(gate: dict[str, Any], *, run_id: str) -> dict[str, Any]:
    gate_id = gate.get("id")
    return {
        "id": gate_id,
        "runId": run_id,
        "branchId": gate.get("branchId") or "",
        "label": gate.get("label") or gate_id,
        "status": gate.get("status") or "pending",
        "value": gate.get("value") or "",
        "summary": gate.get("summary") or "",
        "threshold": gate.get("threshold") or "",
        "input": gate.get("input") or "",
        "toolCallIds": gate.get("toolCallIds") or [],
        "artifactIds": gate.get("artifactIds") or [],
        "failureReason": gate.get("failureReason") or "",
        "remediation": gate.get("remediation") or "",
        "uri": f"worldline-run-ledger://{run_id}/gates/{gate_id}",
    }


def _source_id_for_evidence(evidence: dict[str, Any]) -> str:
    source_ref = evidence.get("sourceRef") if isinstance(evidence.get("sourceRef"), dict) else {}
    return str(
        source_ref.get("id")
        or evidence.get("sourceAssetId")
        or evidence.get("sourceUri")
        or evidence.get("evidenceId")
        or evidence.get("id")
        or ""
    )


def _evidence_source_id(view: dict[str, Any]) -> str:
    source_ref = view.get("sourceRef") if isinstance(view.get("sourceRef"), dict) else {}
    return str(source_ref.get("id") or view.get("sourceId") or view.get("sourceUri") or "")


def _as_evidence_view(evidence: dict[str, Any], *, run_id: str) -> dict[str, Any]:
    evidence_id = evidence.get("evidenceId") or evidence.get("id")
    source_ref = evidence.get("sourceRef") if isinstance(evidence.get("sourceRef"), dict) else {}
    source_id = _source_id_for_evidence(evidence)
    return {
        "id": evidence.get("id") or evidence_id,
        "evidenceId": evidence_id,
        "runId": run_id,
        "title": evidence.get("title") or evidence_id,
        "type": evidence.get("type") or "evidence",
        "typeLabel": evidence.get("typeLabel") or "EvidenceAnchor",
        "summary": evidence.get("summary") or "",
        "sourceId": source_id,
        "sourceUri": evidence.get("sourceUri") or source_ref.get("sourceUri") or "",
        "lineStart": evidence.get("lineStart"),
        "lineEnd": evidence.get("lineEnd"),
        "page": evidence.get("page"),
        "bbox": evidence.get("bbox"),
        "sourceRef": source_ref,
        "documentNode": {
            "id": source_ref.get("documentNodeId") or "",
            "label": source_ref.get("documentNodeLabel") or "",
        },
        "uri": f"worldline-run-ledger://{run_id}/evidence/{evidence_id}",
        "sourceUriRef": f"worldline-run-ledger://{run_id}/sources/{source_id}" if source_id else "",
    }


def _knowledge_item_matches(item: dict[str, Any], item_id: str) -> bool:
    candidates = {
        str(item.get("id") or ""),
        str(item.get("slug") or ""),
        str(item.get("name") or ""),
        str(item.get("label") or ""),
    }
    return str(item_id or "") in candidates


def _as_knowledge_view(item: dict[str, Any], *, run_id: str) -> dict[str, Any]:
    kind = str(item.get("kind") or "wiki")
    if kind == "wiki":
        item_id = item.get("id") or item.get("slug")
        label = item.get("title") or item.get("slug") or item_id
        view = {
            "id": item_id,
            "kind": "wiki",
            "runId": run_id,
            "label": label,
            "title": item.get("title") or label,
            "slug": item.get("slug") or "",
            "status": item.get("status") or "draft",
            "summary": item.get("summary") or "",
            "evidenceCoverage": item.get("evidenceCoverage") or 0,
            "evidenceIds": item.get("evidenceIds") or [],
        }
    elif kind == "graph":
        item_id = item.get("id") or item.get("name")
        label = item.get("name") or item_id
        view = {
            "id": item_id,
            "kind": "graph",
            "runId": run_id,
            "label": label,
            "name": item.get("name") or label,
            "type": item.get("type") or "entity",
            "summary": item.get("summary") or "",
            "confidence": item.get("confidence") or 0,
            "evidenceId": item.get("evidenceId") or "",
        }
    else:
        item_id = item.get("id") or item.get("label")
        label = item.get("label") or item_id
        view = {
            "id": item_id,
            "kind": "timeline",
            "runId": run_id,
            "label": label,
            "status": item.get("status") or "observed",
            "summary": item.get("summary") or "",
            "validFrom": item.get("validFrom") or "",
            "validTo": item.get("validTo") or "",
            "evidenceId": item.get("evidenceId") or "",
        }
    view["uri"] = f"worldline-run-ledger://{run_id}/{view['kind']}/{view['id']}"
    return view


def _manifest_resource(item: dict[str, Any], *, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item.get("id") or item.get("evidenceId") or item.get("sourceId") or "",
        "label": item.get("label") or item.get("title") or item.get("name") or item.get("summary") or item.get("id") or "",
        "kind": item.get("kind") or item.get("type") or "",
        "uri": item.get("uri") or item.get("sourceUriRef") or "",
        "tool": tool_name,
        "args": args,
        "summary": item.get("summary") or "",
    }


def _manifest_section(
    run_id: str,
    *,
    section_id: str,
    label: str,
    tool_name: str,
    uri_segment: str,
    resources: list[dict[str, Any]],
    include_resources: bool,
) -> dict[str, Any]:
    return {
        "id": section_id,
        "label": label,
        "tool": tool_name,
        "uri": f"worldline-run-ledger://{run_id}/{uri_segment}",
        "count": len(resources),
        "resources": resources if include_resources else [],
    }


def _manifest_knowledge_section(
    run_id: str,
    kind: str,
    label: str,
    items: list[dict[str, Any]],
    *,
    include_resources: bool,
) -> dict[str, Any]:
    return _manifest_section(
        run_id,
        section_id=kind,
        label=label,
        tool_name="worldline.inspect_run_knowledge",
        uri_segment=kind,
        resources=[
            _manifest_resource(
                item,
                tool_name="worldline.inspect_run_knowledge",
                args={"run_id": run_id, "kind": kind, "item_id": item.get("id") or kind, "audit_db_id": ""},
            )
            for item in items
        ],
        include_resources=include_resources,
    )


def _source_manifest_views(evidence_items: list[dict[str, Any]], *, run_id: str) -> list[dict[str, Any]]:
    seen: set[str] = set()
    sources: list[dict[str, Any]] = []
    for evidence in evidence_items:
        source_ref = evidence.get("sourceRef") if isinstance(evidence.get("sourceRef"), dict) else {}
        source_id = str(evidence.get("sourceId") or source_ref.get("id") or evidence.get("sourceUri") or "").strip()
        if not source_id or source_id in seen:
            continue
        seen.add(source_id)
        label = source_ref.get("label") or evidence.get("sourceUri") or source_id
        sources.append(
            {
                "id": source_id,
                "kind": source_ref.get("kind") or "source",
                "label": label,
                "summary": source_ref.get("role") or evidence.get("summary") or "",
                "uri": f"worldline-run-ledger://{run_id}/sources/{source_id}",
                "sourceUri": evidence.get("sourceUri") or "",
                "evidenceId": evidence.get("evidenceId") or evidence.get("id") or "",
                "documentNode": evidence.get("documentNode") or {},
            }
        )
    return sources


def _run_manifest_tools() -> list[dict[str, Any]]:
    return [
        {"name": "worldline.inspect_run_manifest", "write_scope": "none", "dispatch_backend": "inline"},
        {"name": "worldline.inspect_run_artifacts", "write_scope": "none", "dispatch_backend": "inline"},
        {"name": "worldline.inspect_run_gates", "write_scope": "none", "dispatch_backend": "inline"},
        {"name": "worldline.inspect_run_evidence", "write_scope": "none", "dispatch_backend": "inline"},
        {"name": "worldline.inspect_run_knowledge", "write_scope": "none", "dispatch_backend": "inline"},
    ]


def _artifact_content_summary(content: Any) -> dict[str, Any]:
    if not isinstance(content, dict):
        return {}
    return {
        "protocol": content.get("protocol") or "",
        "run_title": (content.get("run") or {}).get("title") if isinstance(content.get("run"), dict) else "",
        "selected_event": (content.get("selectedEvent") or {}).get("label")
        if isinstance(content.get("selectedEvent"), dict)
        else "",
        "focused_dossier": (content.get("focusedDossier") or {}).get("title")
        if isinstance(content.get("focusedDossier"), dict)
        else "",
        "replay_steps": len(content.get("replayTimeline") or []) if isinstance(content.get("replayTimeline"), list) else 0,
        "counts": content.get("counts") if isinstance(content.get("counts"), dict) else {},
    }
