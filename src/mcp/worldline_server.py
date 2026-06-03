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
        return await WorldlineAgentWorkflowService().plan_workflow(db_id, workflow_type=workflow_type)

    @server.tool()
    async def worldline_rebuild_wiki(db_id: str, file_id: str | None = None, max_topics: int = 8) -> dict[str, Any]:
        """Rebuild Auto-Wiki pages through the controlled service boundary."""
        return await AutoWikiService().rebuild_wiki(db_id, file_id=file_id, max_topics=max_topics)

    @server.tool()
    async def worldline_update_graph(db_id: str, max_entities: int = 40) -> dict[str, Any]:
        """Extract evidence-bound graph and temporal artifacts."""
        return await KnowledgeGraphService().rebuild_graph(db_id, max_entities=max_entities)

    @server.tool()
    async def worldline_run_quality_gate(db_id: str, thresholds: dict[str, Any] | None = None) -> dict[str, Any]:
        """Run the deterministic Worldline quality gate."""
        return await WorldlineQualityGateService().run_gate(db_id, thresholds=thresholds or {})

    return server


def main() -> None:
    create_server().run()


if __name__ == "__main__":
    main()
