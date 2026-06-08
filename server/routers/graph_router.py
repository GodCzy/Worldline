import traceback
from importlib import import_module

from fastapi import APIRouter, Body, Depends, HTTPException, Query

from server.utils.auth_middleware import get_admin_user
from src import graph_base as _initial_graph_base, knowledge_base
from src.knowledge.graphs.adapters.base import GraphAdapter
from src.knowledge.graphs.adapters.factory import GraphAdapterFactory
from src.storage.postgres.models_business import User
from src.storage.minio.client import StorageError
from src.utils.logging_config import logger

graph = APIRouter(prefix="/graph", tags=["graph"])
graph_base = _initial_graph_base


# =============================================================================
# === 统一图谱接口 (Unified Graph API) ===
# =============================================================================


def _empty_graph_payload(db_id: str, reason: str) -> dict:
    return {
        "nodes": [],
        "edges": [],
        "available": False,
        "degraded": True,
        "degraded_reason": reason,
        "database_id": db_id,
        "graph_type": "upload" if db_id == "neo4j" else "lightrag",
    }


def _empty_stats_payload(db_id: str, reason: str) -> dict:
    return {
        "total_nodes": 0,
        "total_edges": 0,
        "entity_types": [],
        "available": False,
        "degraded": True,
        "degraded_reason": reason,
        "database_id": db_id,
    }


def _neo4j_unavailable_info(reason: str) -> dict:
    return {
        "graph_name": "neo4j",
        "entity_count": 0,
        "relationship_count": 0,
        "triples_count": 0,
        "labels": [],
        "status": "unavailable",
        "available": False,
        "degraded": True,
        "degraded_reason": reason,
        "embed_model_name": None,
        "embed_model_configurable": False,
        "unindexed_node_count": 0,
    }


def _set_global_graph_base(candidate) -> None:
    global graph_base
    graph_base = candidate
    try:
        import src as src_module
        import src.knowledge as knowledge_module

        src_module.graph_base = candidate
        knowledge_module.graph_base = candidate
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"Failed to sync recovered graph_base: {exc}")


def _get_graph_base(recover: bool = False):
    if graph_base is not None:
        return graph_base

    if not recover:
        return None

    try:
        import src as src_module
        import src.knowledge as knowledge_module

        candidate = getattr(src_module, "graph_base", None) or getattr(knowledge_module, "graph_base", None)
        if candidate is not None:
            _set_global_graph_base(candidate)
            return candidate

        upload_service_cls = getattr(knowledge_module, "UploadGraphService", None)
        if upload_service_cls is None:
            graph_module = import_module("src.knowledge.graphs.upload_graph_service")
            upload_service_cls = getattr(graph_module, "UploadGraphService")

        candidate = upload_service_cls()
        _set_global_graph_base(candidate)
        logger.info("Recovered graph_base after delayed Neo4j availability")
        return candidate
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"Neo4j graph service is unavailable: {exc}")
        return None


def _ensure_graph_base_running():
    candidate = _get_graph_base(recover=True)
    if candidate is None:
        return None, "Neo4j graph service is not initialized"

    try:
        if candidate.is_running():
            return candidate, None
        candidate.start()
        if candidate.is_running():
            return candidate, None
        return None, f"Neo4j graph service status is {getattr(candidate, 'status', 'unknown')}"
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"Neo4j graph service is not running: {exc}")
        return None, str(exc)


async def _get_graph_adapter(db_id: str) -> GraphAdapter:
    """
    根据数据库ID获取对应的图谱适配器

    Args:
        db_id: 数据库ID

    Returns:
        GraphAdapter: 对应的图谱适配器实例
    """
    graph_type = await GraphAdapterFactory.detect_graph_type(db_id, knowledge_base)
    running_graph_base = None

    if graph_type == "upload":
        running_graph_base, reason = _ensure_graph_base_running()
        if running_graph_base is None:
            raise HTTPException(status_code=503, detail=f"Graph database service is unavailable: {reason}")

    try:
        if graph_type == "lightrag":
            return GraphAdapterFactory.create_adapter("lightrag", config={"kb_id": db_id})
        return GraphAdapterFactory.create_adapter(
            "upload",
            graph_db_instance=running_graph_base,
            config={"kgdb_name": db_id},
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning(f"Graph adapter unavailable for {db_id}: {exc}")
        raise HTTPException(status_code=503, detail=f"Graph adapter is unavailable: {exc}") from exc


def _get_capabilities_from_metadata(metadata) -> dict:
    """从 GraphMetadata 对象提取 capabilities 字典"""
    return {
        "supports_embedding": metadata.supports_embedding,
        "supports_threshold": metadata.supports_threshold,
    }


@graph.get("/list")
async def get_graphs(current_user: User = Depends(get_admin_user)):
    """
    获取所有可用的知识图谱列表

    Returns:
        包含所有图谱信息的列表 (包括 Neo4j 和 LightRAG)，以及每个类型的 capability 信息
    """
    try:
        graphs = []

        # 1. 获取默认 Neo4j 图谱信息 (Upload 类型)
        running_graph_base, neo4j_reason = _ensure_graph_base_running()
        if running_graph_base is not None:
            neo4j_info = running_graph_base.get_graph_info() or _neo4j_unavailable_info(
                "Neo4j graph info is unavailable"
            )
        else:
            neo4j_info = _neo4j_unavailable_info(neo4j_reason or "Neo4j graph service is unavailable")
        if neo4j_info:
            # 直接使用 Upload 适配器的默认 metadata
            from src.knowledge.graphs.adapters.upload import UploadGraphAdapter

            capabilities = _get_capabilities_from_metadata(UploadGraphAdapter._get_metadata(None))

            graphs.append(
                {
                    "id": "neo4j",
                    "name": "默认图谱",
                    "type": "upload",
                    "description": "Default graph database for uploaded documents",
                    "status": neo4j_info.get("status", "unknown"),
                    "available": neo4j_info.get("available", neo4j_info.get("status") == "open"),
                    "degraded": neo4j_info.get("degraded", False),
                    "degraded_reason": neo4j_info.get("degraded_reason"),
                    "created_at": neo4j_info.get("last_updated"),
                    "node_count": neo4j_info.get("entity_count", 0),
                    "edge_count": neo4j_info.get("relationship_count", 0),
                    "capabilities": capabilities,
                }
            )

        # 2. 获取 LightRAG 数据库信息
        lightrag_dbs = await knowledge_base.get_lightrag_databases()
        # 直接使用 LightRAG 适配器的默认 metadata
        from src.knowledge.graphs.adapters.lightrag import LightRAGGraphAdapter

        capabilities = _get_capabilities_from_metadata(LightRAGGraphAdapter._get_metadata(None))

        for db in lightrag_dbs:
            db_id = db.get("db_id")

            graphs.append(
                {
                    "id": db_id,
                    "name": db.get("name"),
                    "type": "lightrag",
                    "description": db.get("description"),
                    "status": "active",  # LightRAG DBs are usually active if listed
                    "created_at": db.get("created_at"),
                    "metadata": db,
                    "capabilities": capabilities,
                }
            )

        return {"success": True, "data": graphs}

    except Exception as e:
        logger.error(f"Failed to list graphs: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to list graphs: {str(e)}")


@graph.get("/subgraph")
async def get_subgraph(
    db_id: str = Query(..., description="知识图谱ID"),
    node_label: str = Query("*", description="节点标签或查询关键词"),
    max_depth: int = Query(2, description="最大深度", ge=1, le=5),
    max_nodes: int = Query(100, description="最大节点数", ge=1, le=1000),
    current_user: User = Depends(get_admin_user),
):
    """
    统一的子图查询接口

    Args:
        db_id: 图谱ID (LightRAG DB ID 或 "neo4j")
        node_label: 查询关键词或标签
        max_depth: 扩展深度
        max_nodes: 返回最大节点数
    """
    try:
        logger.info(f"Querying subgraph - db_id: {db_id}, label: {node_label}")

        adapter = await _get_graph_adapter(db_id)

        # 统一查询参数 - 适配器会根据自己的配置处理这些参数
        query_kwargs = {
            "keyword": node_label,
            "max_depth": max_depth,
            "max_nodes": max_nodes,
        }

        result_data = await adapter.query_nodes(**query_kwargs)

        return {
            "success": True,
            "data": result_data,
        }

    except HTTPException as exc:
        if exc.status_code == 503:
            return {
                "success": True,
                "data": _empty_graph_payload(db_id, str(exc.detail)),
                "degraded": True,
                "message": str(exc.detail),
            }
        raise
    except Exception as e:
        logger.error(f"Failed to get subgraph: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to get subgraph: {str(e)}")


@graph.get("/labels")
async def get_graph_labels(
    db_id: str = Query(..., description="知识图谱ID"), current_user: User = Depends(get_admin_user)
):
    """
    获取图谱的所有标签
    """
    try:
        # 使用统一的适配器获取标签
        adapter = await _get_graph_adapter(db_id)
        labels = await adapter.get_labels()
        return {"success": True, "data": {"labels": labels}}

    except HTTPException as exc:
        if exc.status_code == 503:
            return {
                "success": True,
                "data": {
                    "labels": [],
                    "available": False,
                    "degraded": True,
                    "degraded_reason": str(exc.detail),
                    "database_id": db_id,
                },
                "degraded": True,
                "message": str(exc.detail),
            }
        raise
    except Exception as e:
        logger.error(f"Failed to get labels: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get labels: {str(e)}")


@graph.get("/stats")
async def get_graph_stats(
    db_id: str = Query(..., description="知识图谱ID"), current_user: User = Depends(get_admin_user)
):
    """
    获取图谱统计信息
    """
    try:
        # 使用适配器的统计信息 (适用于 kb_ 开头的数据库和 LightRAG 数据库)
        if db_id.startswith("kb_") or await knowledge_base.is_lightrag_database(db_id):
            adapter = await _get_graph_adapter(db_id)
            stats_data = await adapter.get_stats()
            return {"success": True, "data": stats_data}
        else:
            # Neo4j stats (直接管理的图谱)
            running_graph_base, reason = _ensure_graph_base_running()
            if running_graph_base is None:
                return {
                    "success": True,
                    "data": _empty_stats_payload(db_id, reason or "Neo4j graph service is unavailable"),
                    "degraded": True,
                    "message": reason,
                }

            info = running_graph_base.get_graph_info(graph_name=db_id)
            if not info:
                raise HTTPException(status_code=404, detail="Graph info not found")

            return {
                "success": True,
                "data": {
                    "total_nodes": info.get("entity_count", 0),
                    "total_edges": info.get("relationship_count", 0),
                    # Neo4j info currently returns 'labels' list, not counts per label.
                    # Improving this would require updating GraphDatabase.get_graph_info
                    "entity_types": [{"type": label, "count": "N/A"} for label in info.get("labels", [])],
                },
            }

    except HTTPException as exc:
        if exc.status_code == 503:
            return {
                "success": True,
                "data": _empty_stats_payload(db_id, str(exc.detail)),
                "degraded": True,
                "message": str(exc.detail),
            }
        raise
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@graph.get("/neo4j/nodes")
async def get_neo4j_nodes(
    kgdb_name: str = Query(..., description="知识图谱数据库名称"),
    num: int = Query(100, description="节点数量", ge=1, le=1000),
    current_user: User = Depends(get_admin_user),
):
    """(Deprecated) Use /graph/subgraph instead"""
    response = await get_subgraph(db_id=kgdb_name, node_label="*", max_nodes=num, current_user=current_user)
    return {"success": True, "result": response["data"], "message": "success"}


@graph.get("/neo4j/node")
async def get_neo4j_node(
    entity_name: str = Query(..., description="实体名称"), current_user: User = Depends(get_admin_user)
):
    """(Deprecated) Use /graph/subgraph instead"""
    # neo4j/node uses query_nodes(keyword=entity_name)
    response = await get_subgraph(db_id="neo4j", node_label=entity_name, current_user=current_user)
    return {"success": True, "result": response["data"], "message": "success"}


@graph.get("/neo4j/info")
async def get_neo4j_info(current_user: User = Depends(get_admin_user)):
    """获取Neo4j图数据库信息"""
    try:
        running_graph_base, reason = _ensure_graph_base_running()
        if running_graph_base is None:
            return {
                "success": True,
                "data": _neo4j_unavailable_info(reason or "Neo4j graph service is unavailable"),
                "degraded": True,
                "message": reason,
            }

        graph_info = running_graph_base.get_graph_info()
        if graph_info is None:
            return {
                "success": True,
                "data": _neo4j_unavailable_info("Neo4j graph info is unavailable"),
                "degraded": True,
                "message": "Neo4j graph info is unavailable",
            }
        return {"success": True, "data": graph_info}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取图数据库信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取图数据库信息失败: {str(e)}")


@graph.post("/neo4j/index-entities")
async def index_neo4j_entities(data: dict = Body(default={}), current_user: User = Depends(get_admin_user)):
    """为Neo4j图谱节点添加嵌入向量索引"""
    try:
        running_graph_base, reason = _ensure_graph_base_running()
        if running_graph_base is None:
            raise HTTPException(status_code=503, detail=f"Graph database service is unavailable: {reason}")

        kgdb_name = data.get("kgdb_name", "neo4j")
        count = await running_graph_base.add_embedding_to_nodes(kgdb_name=kgdb_name)

        return {
            "success": True,
            "status": "success",
            "message": f"已成功为{count}个节点添加嵌入向量",
            "indexed_count": count,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"索引节点失败: {e}")
        raise HTTPException(status_code=500, detail=f"索引节点失败: {str(e)}")


@graph.post("/neo4j/add-entities")
async def add_neo4j_entities(
    file_path: str = Body(...),
    kgdb_name: str | None = Body(None),
    embed_model_name: str | None = Body(None),
    batch_size: int | None = Body(None),
    current_user: User = Depends(get_admin_user),
):
    """通过JSONL文件添加图谱实体到Neo4j（只接受 MinIO URL）"""
    try:
        # 服务层会验证 URL 并从 MinIO 下载文件
        running_graph_base, reason = _ensure_graph_base_running()
        if running_graph_base is None:
            raise HTTPException(status_code=503, detail=f"Graph database service is unavailable: {reason}")

        await running_graph_base.jsonl_file_add_entity(file_path, kgdb_name, embed_model_name, batch_size)
        return {"success": True, "message": "实体添加成功", "status": "success"}
    except HTTPException:
        raise
    except StorageError as e:
        # MinIO 验证或下载错误
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        # 本地路径拒绝错误
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"添加实体失败: {e}, {traceback.format_exc()}")
        return {"success": False, "message": f"添加实体失败: {e}", "status": "failed"}
