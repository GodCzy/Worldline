from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

from src.storage.postgres.models_business import Base
from src.storage.postgres.models_knowledge import (
    DocumentNode,
    DocumentVersion,
    EvidenceAnchor,
    GoldenSetItem,
    KnowledgeChunk,
    KnowledgeEntity,
    KnowledgeRelationship,
    QualityGateRun,
    SourceAsset,
    TemporalFact,
    WikiPage,
    WorldlineMcpAuditLog,
    WorldlineWorkflowRun,
)


def test_phase1_knowledge_object_tables_are_registered() -> None:
    expected_tables = {
        "source_assets",
        "document_versions",
        "document_nodes",
        "evidence_anchors",
        "golden_set_items",
        "knowledge_chunks",
        "knowledge_entities",
        "knowledge_relationships",
        "quality_gate_runs",
        "temporal_facts",
        "wiki_pages",
        "worldline_mcp_audit_logs",
        "worldline_workflow_runs",
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


def test_wiki_page_contract_supports_auto_wiki_outputs() -> None:
    table = WikiPage.__table__

    assert table.columns["page_id"].unique is True
    assert table.columns["db_id"].nullable is False
    assert table.columns["page_type"].nullable is False
    assert table.columns["slug"].nullable is False
    assert table.columns["title"].nullable is False
    assert table.columns["markdown"].nullable is False
    assert WikiPage.page_metadata.property.columns[0].name == "metadata"

    fk_targets = {fk.target_fullname for fk in table.foreign_keys}
    assert "knowledge_bases.db_id" in fk_targets

    index_names = {index.name for index in table.indexes}
    assert {
        "idx_wiki_pages_db_type",
        "idx_wiki_pages_db_slug",
        "idx_wiki_pages_source",
    }.issubset(index_names)


def test_knowledge_graph_contract_binds_entities_relationships_and_temporal_facts() -> None:
    entity_table = KnowledgeEntity.__table__
    relationship_table = KnowledgeRelationship.__table__
    fact_table = TemporalFact.__table__

    assert entity_table.columns["entity_id"].unique is True
    assert entity_table.columns["db_id"].nullable is False
    assert entity_table.columns["name"].nullable is False
    assert KnowledgeEntity.entity_metadata.property.columns[0].name == "metadata"

    assert relationship_table.columns["relationship_id"].unique is True
    assert relationship_table.columns["source_entity_id"].nullable is False
    assert relationship_table.columns["target_entity_id"].nullable is False
    assert relationship_table.columns["relation_type"].nullable is False
    assert KnowledgeRelationship.relationship_metadata.property.columns[0].name == "metadata"

    assert fact_table.columns["fact_id"].unique is True
    assert fact_table.columns["subject"].nullable is False
    assert fact_table.columns["object"].nullable is False
    assert fact_table.columns["occurred_at"].nullable is False
    assert TemporalFact.fact_metadata.property.columns[0].name == "metadata"

    fk_targets = {
        *(fk.target_fullname for fk in entity_table.foreign_keys),
        *(fk.target_fullname for fk in relationship_table.foreign_keys),
        *(fk.target_fullname for fk in fact_table.foreign_keys),
    }
    assert "knowledge_bases.db_id" in fk_targets
    assert "knowledge_entities.entity_id" in fk_targets

    index_names = {
        *(index.name for index in entity_table.indexes),
        *(index.name for index in relationship_table.indexes),
        *(index.name for index in fact_table.indexes),
    }
    assert {
        "idx_knowledge_entities_db_name",
        "idx_knowledge_entities_db_type",
        "idx_knowledge_relationships_db_type",
        "idx_knowledge_relationships_source",
        "idx_knowledge_relationships_target",
        "idx_temporal_facts_db_time",
        "idx_temporal_facts_subject",
    }.issubset(index_names)


def test_workflow_and_quality_gate_contract_supports_phase6_and_phase7() -> None:
    golden_table = GoldenSetItem.__table__
    gate_table = QualityGateRun.__table__
    workflow_table = WorldlineWorkflowRun.__table__

    assert golden_table.columns["item_id"].unique is True
    assert golden_table.columns["query"].nullable is False
    assert GoldenSetItem.item_metadata.property.columns[0].name == "metadata"

    assert gate_table.columns["gate_id"].unique is True
    assert gate_table.columns["status"].nullable is False
    assert "metrics" in gate_table.columns
    assert "coverage_map" in gate_table.columns
    assert "failure_replay" in gate_table.columns
    assert "tracing" in gate_table.columns
    assert "cost_stats" in gate_table.columns
    assert "latency_stats" in gate_table.columns
    assert "permission_checks" in gate_table.columns

    assert workflow_table.columns["workflow_id"].unique is True
    assert workflow_table.columns["orchestrator"].nullable is False
    assert workflow_table.columns["dispatch_backend"].nullable is False
    assert "steps" in workflow_table.columns
    assert "trace" in workflow_table.columns

    fk_targets = {
        *(fk.target_fullname for fk in golden_table.foreign_keys),
        *(fk.target_fullname for fk in gate_table.foreign_keys),
        *(fk.target_fullname for fk in workflow_table.foreign_keys),
    }
    assert "knowledge_bases.db_id" in fk_targets

    index_names = {
        *(index.name for index in golden_table.indexes),
        *(index.name for index in gate_table.indexes),
        *(index.name for index in workflow_table.indexes),
    }
    assert {
        "idx_golden_set_items_db_status",
        "idx_quality_gate_runs_db_status",
        "idx_quality_gate_runs_created",
        "idx_worldline_workflow_runs_db_status",
    }.issubset(index_names)


def test_worldline_mcp_audit_log_contract_supports_tool_auditing() -> None:
    table = WorldlineMcpAuditLog.__table__

    assert table.columns["log_id"].unique is True
    assert table.columns["db_id"].nullable is False
    assert table.columns["tool_name"].nullable is False
    assert table.columns["status"].nullable is False
    assert WorldlineMcpAuditLog.audit_metadata.property.columns[0].name == "metadata"

    fk_targets = {fk.target_fullname for fk in table.foreign_keys}
    assert "knowledge_bases.db_id" in fk_targets

    index_names = {index.name for index in table.indexes}
    assert {
        "idx_worldline_mcp_audit_db_tool",
        "idx_worldline_mcp_audit_status",
    }.issubset(index_names)


def test_phase1_tables_compile_to_postgresql_ddl() -> None:
    dialect = postgresql.dialect()

    for model in (
        SourceAsset,
        DocumentVersion,
        DocumentNode,
        EvidenceAnchor,
        KnowledgeChunk,
        WikiPage,
        KnowledgeEntity,
        KnowledgeRelationship,
        TemporalFact,
        GoldenSetItem,
        QualityGateRun,
        WorldlineWorkflowRun,
        WorldlineMcpAuditLog,
    ):
        ddl = str(CreateTable(model.__table__).compile(dialect=dialect))
        assert f"CREATE TABLE {model.__tablename__}" in ddl
        assert "JSONB" in ddl
