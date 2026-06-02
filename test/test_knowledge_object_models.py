from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

from src.storage.postgres.models_business import Base
from src.storage.postgres.models_knowledge import (
    DocumentNode,
    DocumentVersion,
    EvidenceAnchor,
    KnowledgeChunk,
    SourceAsset,
)


def test_phase1_knowledge_object_tables_are_registered() -> None:
    expected_tables = {
        "source_assets",
        "document_versions",
        "document_nodes",
        "evidence_anchors",
        "knowledge_chunks",
    }

    assert expected_tables.issubset(Base.metadata.tables.keys())


def test_source_asset_contract_columns_and_indexes() -> None:
    table = SourceAsset.__table__

    expected_columns = {
        "id",
        "asset_id",
        "db_id",
        "asset_type",
        "uri",
        "title",
        "content_hash",
        "owner",
        "status",
        "metadata",
        "created_at",
        "updated_at",
    }

    assert expected_columns.issubset(table.columns.keys())
    assert table.columns["asset_id"].unique is True
    assert table.columns["asset_type"].nullable is False
    assert table.columns["uri"].nullable is False
    assert SourceAsset.asset_metadata.property.columns[0].name == "metadata"

    index_names = {index.name for index in table.indexes}
    assert {"idx_source_assets_db_type", "idx_source_assets_hash"}.issubset(index_names)


def test_document_version_contract_links_source_asset_and_knowledge_file() -> None:
    table = DocumentVersion.__table__

    assert table.columns["doc_version_id"].unique is True
    assert table.columns["asset_id"].nullable is False
    assert table.columns["parser"].nullable is False
    assert table.columns["status"].nullable is False

    fk_targets = {fk.target_fullname for fk in table.foreign_keys}
    assert "source_assets.asset_id" in fk_targets
    assert "knowledge_files.file_id" in fk_targets

    index_names = {index.name for index in table.indexes}
    assert {"idx_document_versions_asset_status", "idx_document_versions_ast_hash"}.issubset(index_names)


def test_document_node_contract_preserves_ast_structure() -> None:
    table = DocumentNode.__table__

    assert table.columns["node_id"].unique is True
    assert table.columns["doc_version_id"].nullable is False
    assert table.columns["node_type"].nullable is False
    assert table.columns["node_order"].nullable is False
    assert DocumentNode.node_metadata.property.columns[0].name == "metadata"

    fk_targets = {fk.target_fullname for fk in table.foreign_keys}
    assert "document_versions.doc_version_id" in fk_targets
    assert "document_nodes.node_id" in fk_targets

    index_names = {index.name for index in table.indexes}
    assert {
        "idx_document_nodes_version_order",
        "idx_document_nodes_version_type",
        "idx_document_nodes_parent",
    }.issubset(index_names)


def test_evidence_anchor_contract_requires_document_node_traceability() -> None:
    table = EvidenceAnchor.__table__

    assert table.columns["evidence_id"].unique is True
    assert table.columns["doc_version_id"].nullable is False
    assert table.columns["node_id"].nullable is False
    assert table.columns["source_uri"].nullable is False
    assert table.columns["anchor_type"].nullable is False
    assert EvidenceAnchor.evidence_metadata.property.columns[0].name == "metadata"

    fk_targets = {fk.target_fullname for fk in table.foreign_keys}
    assert "document_versions.doc_version_id" in fk_targets
    assert "document_nodes.node_id" in fk_targets

    index_names = {index.name for index in table.indexes}
    assert {
        "idx_evidence_anchors_doc_node",
        "idx_evidence_anchors_page",
        "idx_evidence_anchors_anchor_type",
    }.issubset(index_names)


def test_knowledge_chunk_contract_binds_chunks_to_evidence() -> None:
    table = KnowledgeChunk.__table__

    assert table.columns["chunk_id"].unique is True
    assert table.columns["db_id"].nullable is False
    assert table.columns["file_id"].nullable is False
    assert table.columns["doc_version_id"].nullable is False
    assert table.columns["text"].nullable is False
    assert KnowledgeChunk.chunk_metadata.property.columns[0].name == "metadata"

    fk_targets = {fk.target_fullname for fk in table.foreign_keys}
    assert "knowledge_bases.db_id" in fk_targets
    assert "knowledge_files.file_id" in fk_targets
    assert "document_versions.doc_version_id" in fk_targets

    index_names = {index.name for index in table.indexes}
    assert {
        "idx_knowledge_chunks_db_file",
        "idx_knowledge_chunks_doc_version",
        "idx_knowledge_chunks_order",
    }.issubset(index_names)


def test_phase1_tables_compile_to_postgresql_ddl() -> None:
    dialect = postgresql.dialect()

    for model in (SourceAsset, DocumentVersion, DocumentNode, EvidenceAnchor, KnowledgeChunk):
        ddl = str(CreateTable(model.__table__).compile(dialect=dialect))
        assert f"CREATE TABLE {model.__tablename__}" in ddl
        assert "JSONB" in ddl
