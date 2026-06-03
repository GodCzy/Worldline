from __future__ import annotations

from typing import Any

from src.services.auto_wiki_service import AutoWikiService
from src.services.knowledge_graph_service import KnowledgeGraphService
from src.services.worldline_agent_workflow_service import WorldlineAgentWorkflowService
from src.services.worldline_quality_gate_service import WorldlineQualityGateService


def get_manifest() -> dict[str, Any]:
    return WorldlineAgentWorkflowService().tool_manifest()


def create_server():
    try:
        from mcp.server.fastmcp import FastMCP
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("mcp package is required to run the Worldline MCP server") from exc

    server = FastMCP("worldline")

    @server.tool()
    async def worldline_manifest() -> dict[str, Any]:
        """Return the controlled Worldline MCP tool manifest."""
        return get_manifest()

    @server.tool()
    async def worldline_plan_workflow(db_id: str, workflow_type: str = "knowledge_refresh") -> dict[str, Any]:
        """Plan a LangGraph-shaped workflow with ARQ dispatch metadata."""
        return await WorldlineAgentWorkflowService().plan_workflow(db_id, workflow_type=workflow_type, created_by="mcp")

    @server.tool()
    async def worldline_rebuild_wiki(db_id: str, file_id: str | None = None, max_topics: int = 8) -> dict[str, Any]:
        """Rebuild Auto-Wiki pages through the controlled service boundary."""
        result = await AutoWikiService().rebuild_wiki(db_id, file_id=file_id, max_topics=max_topics)
        await WorldlineAgentWorkflowService().audit_tool_call(
            db_id,
            tool_name="worldline.rebuild_wiki",
            actor="mcp",
            request_summary={"file_id": file_id, "max_topics": max_topics},
            result_summary={"status": result.get("status"), "page_counts": result.get("page_counts")},
        )
        return result

    @server.tool()
    async def worldline_update_graph(db_id: str, max_entities: int = 40) -> dict[str, Any]:
        """Extract evidence-bound graph and temporal artifacts."""
        result = await KnowledgeGraphService().rebuild_graph(db_id, max_entities=max_entities)
        await WorldlineAgentWorkflowService().audit_tool_call(
            db_id,
            tool_name="worldline.update_graph",
            actor="mcp",
            request_summary={"max_entities": max_entities},
            result_summary={"status": result.get("status"), "counts": result.get("counts")},
        )
        return result

    @server.tool()
    async def worldline_run_quality_gate(db_id: str, thresholds: dict[str, Any] | None = None) -> dict[str, Any]:
        """Run the deterministic Worldline quality gate."""
        result = await WorldlineQualityGateService().run_gate(db_id, thresholds=thresholds or {}, created_by="mcp")
        await WorldlineAgentWorkflowService().audit_tool_call(
            db_id,
            tool_name="worldline.run_quality_gate",
            actor="mcp",
            request_summary={"thresholds": thresholds or {}},
            result_summary={"status": result.get("status"), "gate_id": result.get("gate_id")},
        )
        return result

    return server


def main() -> None:
    create_server().run()


if __name__ == "__main__":
    main()
