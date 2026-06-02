import os
from importlib import import_module

from ..config import config
from .factory import KnowledgeBaseFactory
from .manager import KnowledgeBaseManager
from src.utils.logging_config import logger


def _register_kb_type(kb_type: str, module_path: str, class_name: str, description: str) -> None:
    try:
        module = import_module(module_path, package=__name__)
        kb_class = getattr(module, class_name)
        KnowledgeBaseFactory.register(kb_type, kb_class, {"description": description})
    except ModuleNotFoundError as exc:
        logger.warning(f"Skip registering {kb_type} knowledge base because dependency is unavailable: {exc}")


_register_kb_type(
    "milvus",
    ".implementations.milvus",
    "MilvusKB",
    "基于 Milvus 的生产级向量知识库，适合高性能部署",
)
_register_kb_type(
    "lightrag",
    ".implementations.lightrag",
    "LightRagKB",
    "基于图检索的知识库，支持实体关系构建和复杂查询",
)
_register_kb_type("dify", ".implementations.dify", "DifyKB", "连接 Dify Dataset 的只读检索知识库")

# 创建知识库管理器
work_dir = os.path.join(config.save_dir, "knowledge_base_data")
knowledge_base = KnowledgeBaseManager(work_dir)

# 创建图数据库实例
graph_base = None
UploadGraphService = None
try:
    graph_module = import_module(".graphs.upload_graph_service", package=__name__)
    UploadGraphService = getattr(graph_module, "UploadGraphService")
    graph_base = UploadGraphService()
except Exception as exc:  # noqa: BLE001
    logger.warning(
        "Graph database bootstrap failed during import; continuing without graph_base until runtime recovery: "
        f"{exc}"
    )

# 向后兼容：让 GraphDatabase 指向 UploadGraphService
GraphDatabase = UploadGraphService

__all__ = ["GraphDatabase", "UploadGraphService", "knowledge_base", "graph_base"]
