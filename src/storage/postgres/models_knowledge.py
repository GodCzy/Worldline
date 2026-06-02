"""PostgreSQL 知识库模型 - 知识库、文档编译链、证据锚点和评估相关表。"""

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB

from src.storage.postgres.models_business import Base
from src.utils.datetime_utils import utc_now_naive

JSON_VALUE = JSON().with_variant(JSONB, "postgresql")


class KnowledgeBase(Base):
    """知识库模型"""

    __tablename__ = "knowledge_bases"
    __table_args__ = (UniqueConstraint("db_id", name="uq_knowledge_bases_db_id"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    db_id = Column(String(80), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    kb_type = Column(String(32), nullable=False, index=True)
    embed_info = Column(JSON_VALUE)
    llm_info = Column(JSON_VALUE)
    query_params = Column(JSON_VALUE)
    additional_params = Column(JSON_VALUE)
    share_config = Column(JSON_VALUE)
    mindmap = Column(JSON_VALUE)
    sample_questions = Column(JSON_VALUE)
    created_at = Column(DateTime(timezone=True), default=utc_now_naive)
    updated_at = Column(DateTime(timezone=True), default=utc_now_naive, onupdate=utc_now_naive)


class KnowledgeFile(Base):
    """知识文件模型"""

    __tablename__ = "knowledge_files"
    __table_args__ = (UniqueConstraint("file_id", name="uq_knowledge_files_file_id"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(String(64), unique=True, nullable=False, index=True)
    db_id = Column(String(80), ForeignKey("knowledge_bases.db_id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id = Column(String(64), ForeignKey("knowledge_files.file_id", ondelete="SET NULL"), index=True)
    filename = Column(String(512), nullable=False)
    original_filename = Column(String(512))
    file_type = Column(String(64))
    path = Column(String(1024))
    minio_url = Column(String(1024))
    markdown_file = Column(String(1024))
    status = Column(String(32), default="uploaded", index=True)
    content_hash = Column(String(128), index=True)
    file_size = Column(BigInteger)
    content_type = Column(String(64))
    processing_params = Column(JSON_VALUE)
    is_folder = Column(Boolean, default=False)
    error_message = Column(Text)
    created_by = Column(String(64))
    updated_by = Column(String(64))
    created_at = Column(DateTime(timezone=True), default=utc_now_naive)
    updated_at = Column(DateTime(timezone=True), default=utc_now_naive, onupdate=utc_now_naive)


class SourceAsset(Base):
    """原始知识来源。

    SourceAsset 是文档编译链的入口，覆盖文件、网页、代码仓库、API 和外部 MCP 数据源。
    它不直接等同于现有 KnowledgeFile：KnowledgeFile 仍表示知识库文件管理记录，
    SourceAsset 表示可版本化、可编译、可追溯的来源对象。
    """

    __tablename__ = "source_assets"
    __table_args__ = (
        UniqueConstraint("asset_id", name="uq_source_assets_asset_id"),
        Index("idx_source_assets_db_type", "db_id", "asset_type"),
        Index("idx_source_assets_hash", "content_hash"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(String(80), unique=True, nullable=False, index=True)
    db_id = Column(String(80), ForeignKey("knowledge_bases.db_id", ondelete="CASCADE"), nullable=True, index=True)
    asset_type = Column(String(32), nullable=False, index=True)
    uri = Column(String(2048), nullable=False)
    title = Column(String(512))
    content_hash = Column(String(128), index=True)
    owner = Column(String(128))
    status = Column(String(32), nullable=False, default="active", index=True)
    asset_metadata = Column("metadata", JSON_VALUE)
    created_at = Column(DateTime(timezone=True), default=utc_now_naive, index=True)
    updated_at = Column(DateTime(timezone=True), default=utc_now_naive, onupdate=utc_now_naive)


class DocumentVersion(Base):
    """SourceAsset 的一次文档编译版本。"""

    __tablename__ = "document_versions"
    __table_args__ = (
        UniqueConstraint("doc_version_id", name="uq_document_versions_doc_version_id"),
        Index("idx_document_versions_asset_status", "asset_id", "status"),
        Index("idx_document_versions_ast_hash", "ast_hash"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_version_id = Column(String(80), unique=True, nullable=False, index=True)
    asset_id = Column(String(80), ForeignKey("source_assets.asset_id", ondelete="CASCADE"), nullable=False, index=True)
    file_id = Column(String(64), ForeignKey("knowledge_files.file_id", ondelete="SET NULL"), nullable=True, index=True)
    parser = Column(String(128), nullable=False)
    parser_version = Column(String(128))
    status = Column(String(32), nullable=False, default="pending", index=True)
    ast_hash = Column(String(128), index=True)
    content_hash = Column(String(128), index=True)
    version_index = Column(Integer, nullable=False, default=1)
    parse_config = Column(JSON_VALUE)
    stats = Column(JSON_VALUE)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), default=utc_now_naive, index=True)
    updated_at = Column(DateTime(timezone=True), default=utc_now_naive, onupdate=utc_now_naive)


class DocumentNode(Base):
    """Document AST 节点。"""

    __tablename__ = "document_nodes"
    __table_args__ = (
        UniqueConstraint("node_id", name="uq_document_nodes_node_id"),
        Index("idx_document_nodes_version_order", "doc_version_id", "node_order"),
        Index("idx_document_nodes_version_type", "doc_version_id", "node_type"),
        Index("idx_document_nodes_parent", "parent_id"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(String(96), unique=True, nullable=False, index=True)
    doc_version_id = Column(
        String(80),
        ForeignKey("document_versions.doc_version_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    parent_id = Column(String(96), ForeignKey("document_nodes.node_id", ondelete="SET NULL"), nullable=True)
    node_type = Column(String(64), nullable=False, index=True)
    node_order = Column(Integer, nullable=False, default=0)
    text = Column(Text)
    table_json = Column(JSON_VALUE)
    image_ref = Column(String(1024))
    page_start = Column(Integer)
    page_end = Column(Integer)
    bbox = Column(JSON_VALUE)
    char_start = Column(Integer)
    char_end = Column(Integer)
    node_metadata = Column("metadata", JSON_VALUE)
    created_at = Column(DateTime(timezone=True), default=utc_now_naive, index=True)


class EvidenceAnchor(Base):
    """可追溯证据锚点。

    后续 chunk、实体、关系、Wiki 段落和回答 claim 都应通过 evidence_id 绑定到这里。
    """

    __tablename__ = "evidence_anchors"
    __table_args__ = (
        UniqueConstraint("evidence_id", name="uq_evidence_anchors_evidence_id"),
        Index("idx_evidence_anchors_doc_node", "doc_version_id", "node_id"),
        Index("idx_evidence_anchors_page", "doc_version_id", "page"),
        Index("idx_evidence_anchors_anchor_type", "anchor_type"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    evidence_id = Column(String(96), unique=True, nullable=False, index=True)
    doc_version_id = Column(
        String(80),
        ForeignKey("document_versions.doc_version_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    node_id = Column(
        String(96),
        ForeignKey("document_nodes.node_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    anchor_type = Column(String(32), nullable=False, default="text", index=True)
    source_uri = Column(String(2048), nullable=False)
    page = Column(Integer)
    line_start = Column(Integer)
    line_end = Column(Integer)
    bbox = Column(JSON_VALUE)
    char_start = Column(Integer)
    char_end = Column(Integer)
    text_span = Column(JSON_VALUE)
    text_excerpt = Column(Text)
    confidence = Column(Float)
    evidence_metadata = Column("metadata", JSON_VALUE)
    created_at = Column(DateTime(timezone=True), default=utc_now_naive, index=True)


class EvaluationBenchmark(Base):
    """评估基准模型"""

    __tablename__ = "evaluation_benchmarks"
    __table_args__ = (UniqueConstraint("benchmark_id", name="uq_evaluation_benchmarks_benchmark_id"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    benchmark_id = Column(String(64), unique=True, nullable=False, index=True)
    db_id = Column(String(80), ForeignKey("knowledge_bases.db_id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    question_count = Column(Integer, default=0)
    has_gold_chunks = Column(Boolean, default=False)
    has_gold_answers = Column(Boolean, default=False)
    data_file_path = Column(String(1024))
    created_by = Column(String(64))
    created_at = Column(DateTime(timezone=True), default=utc_now_naive)
    updated_at = Column(DateTime(timezone=True), default=utc_now_naive, onupdate=utc_now_naive)


class EvaluationResult(Base):
    """评估结果模型"""

    __tablename__ = "evaluation_results"
    __table_args__ = (UniqueConstraint("task_id", name="uq_evaluation_results_task_id"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(64), unique=True, nullable=False, index=True)
    db_id = Column(String(80), ForeignKey("knowledge_bases.db_id", ondelete="CASCADE"), nullable=False, index=True)
    benchmark_id = Column(
        String(64),
        ForeignKey("evaluation_benchmarks.benchmark_id", ondelete="SET NULL"),
        index=True,
    )
    status = Column(String(32), default="running", index=True)
    retrieval_config = Column(JSON_VALUE)
    metrics = Column(JSON_VALUE)
    overall_score = Column(Float)
    total_questions = Column(Integer, default=0)
    completed_questions = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True), default=utc_now_naive, index=True)
    completed_at = Column(DateTime(timezone=True))
    created_by = Column(String(64))


class EvaluationResultDetail(Base):
    """评估结果详情模型"""

    __tablename__ = "evaluation_result_details"
    __table_args__ = (UniqueConstraint("task_id", "query_index", name="uq_evaluation_result_details_task_query"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(
        String(64),
        ForeignKey("evaluation_results.task_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    query_index = Column(Integer, nullable=False)
    query_text = Column(Text, nullable=False)
    gold_chunk_ids = Column(JSON_VALUE)
    gold_answer = Column(Text)
    generated_answer = Column(Text)
    retrieved_chunks = Column(JSON_VALUE)
    metrics = Column(JSON_VALUE)
