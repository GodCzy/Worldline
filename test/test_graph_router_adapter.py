from __future__ import annotations

import os
import sys
import types
import importlib.util

import pytest

sys.path.insert(0, os.getcwd())
os.environ.setdefault("WORLDLINE_SKIP_APP_INIT", "1")


def _import_graph_router_with_adapter_stubs(monkeypatch):
    sys.modules.pop("graph_router_under_test", None)

    knowledge_module = types.ModuleType("src.knowledge")
    graphs_module = types.ModuleType("src.knowledge.graphs")
    adapters_module = types.ModuleType("src.knowledge.graphs.adapters")
    base_module = types.ModuleType("src.knowledge.graphs.adapters.base")
    factory_module = types.ModuleType("src.knowledge.graphs.adapters.factory")

    class GraphAdapter:
        pass

    class GraphAdapterFactory:
        pass

    base_module.GraphAdapter = GraphAdapter
    factory_module.GraphAdapterFactory = GraphAdapterFactory

    monkeypatch.setitem(sys.modules, "src.knowledge", knowledge_module)
    monkeypatch.setitem(sys.modules, "src.knowledge.graphs", graphs_module)
    monkeypatch.setitem(sys.modules, "src.knowledge.graphs.adapters", adapters_module)
    monkeypatch.setitem(sys.modules, "src.knowledge.graphs.adapters.base", base_module)
    monkeypatch.setitem(sys.modules, "src.knowledge.graphs.adapters.factory", factory_module)

    module_path = os.path.join(os.getcwd(), "server", "routers", "graph_router.py")
    spec = importlib.util.spec_from_file_location("graph_router_under_test", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["graph_router_under_test"] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.asyncio
async def test_lightrag_adapter_does_not_require_upload_graph_base(monkeypatch):
    """LightRAG graphs must not be blocked by Upload/Neo4j graph_base startup."""
    graph_router = _import_graph_router_with_adapter_stubs(monkeypatch)

    class FakeLightRagAdapter:
        async def query_nodes(self, **kwargs):
            return {"nodes": [{"id": "n1", "name": "LightRAG node"}], "edges": []}

    async def fake_detect_graph_type(db_id, knowledge_base_manager=None):
        return "lightrag"

    def fail_if_called():
        raise AssertionError("Upload graph_base should not be required for LightRAG")

    def fake_create_adapter(graph_type, **kwargs):
        assert graph_type == "lightrag"
        assert kwargs["config"]["kb_id"] == "kb_lightrag"
        return FakeLightRagAdapter()

    monkeypatch.setattr(graph_router.GraphAdapterFactory, "detect_graph_type", fake_detect_graph_type, raising=False)
    monkeypatch.setattr(graph_router.GraphAdapterFactory, "create_adapter", fake_create_adapter, raising=False)
    monkeypatch.setattr(graph_router, "_ensure_graph_base_running", fail_if_called)

    adapter = await graph_router._get_graph_adapter("kb_lightrag")
    result = await adapter.query_nodes(keyword="*")

    assert result["nodes"][0]["name"] == "LightRAG node"


@pytest.mark.asyncio
async def test_lightrag_adapter_creation_failure_degrades(monkeypatch):
    """Adapter initialization failures should be explainable degraded graph data."""
    graph_router = _import_graph_router_with_adapter_stubs(monkeypatch)

    async def fake_detect_graph_type(db_id, knowledge_base_manager=None):
        return "lightrag"

    def fake_create_adapter(graph_type, **kwargs):
        raise RuntimeError("Neo4j unavailable in QA")

    monkeypatch.setattr(graph_router.GraphAdapterFactory, "detect_graph_type", fake_detect_graph_type, raising=False)
    monkeypatch.setattr(graph_router.GraphAdapterFactory, "create_adapter", fake_create_adapter, raising=False)

    payload = await graph_router.get_subgraph(
        db_id="kb_lightrag",
        node_label="*",
        max_nodes=10,
        current_user=object(),
    )

    assert payload["success"] is True
    assert payload["degraded"] is True
    assert payload["data"]["nodes"] == []
    assert payload["data"]["edges"] == []
    assert payload["data"]["degraded"] is True
    assert "Neo4j unavailable in QA" in payload["data"]["degraded_reason"]
