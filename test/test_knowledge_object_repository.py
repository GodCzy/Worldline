from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import func, select

from src.knowledge.base import FileStatus, KnowledgeBase as AbstractKnowledgeBase
from src.knowledge.compiler.models import CompiledDocument, CompiledEvidenceAnchor, CompiledNode
from src.repositories.knowledge_object_repository import KnowledgeObjectRepository
from src.storage.postgres.manager import pg_manager
from src.storage.postgres.models_knowledge import (
    DocumentNode,
    DocumentVersion,
    EvidenceAnchor,
    KnowledgeBase,
    KnowledgeFile,
    SourceAsset,
)


class DummyKnowledgeBase(AbstractKnowledgeBase):
    @property
    def kb_type(self) -> str:
        return "dummy"

    async def _create_kb_instance(self, db_id: str, config: dict):
        return None

    async def _initialize_kb_instance(self, instance) -> None:
        return None

    async def index_file(self, db_id: str, file_id: str, operator_id: str | None = None) -> dict:
        return {}

    async def delete_file(self, db_id: str, file_id: str) -> None:
        return None

    async def get_file_basic_info(self, db_id: str, file_id: str) -> dict:
        return {}

    async def get_file_content(self, db_id: str, file_id: str) -> dict:
        return {}

    async def get_file_info(self, db_id: str, file_id: str) -> dict:
        return {}

    async def update_content(self, db_id: str, file_ids: list[str], params: dict | None = None) -> list[dict]:
        return []

    async def aquery(self, query_text: str, db_id: str, **kwargs) -> str:
        return ""

    def get_query_params_config(self, db_id: str, **kwargs) -> dict:
        return {}


@pytest.fixture()
async def sqlite_pg_manager(monkeypatch, tmp_path: Path):
    if pg_manager.async_engine is not None:
        await pg_manager.close()
    pg_manager.async_engine = None
    pg_manager.AsyncSession = None
    pg_manager._initialized = False
    monkeypatch.setenv("POSTGRES_URL", f"sqlite+aiosqlite:///{tmp_path / 'worldline.db'}")
    pg_manager.initialize()
    await pg_manager.create_tables()
    try:
        yield pg_manager
    finally:
        await pg_manager.close()
        pg_manager.async_engine = None
        pg_manager.AsyncSession = None
        pg_manager._initialized = False


@pytest.mark.asyncio
async def test_repository_persists_compiled_document_objects(sqlite_pg_manager) -> None:
    async with sqlite_pg_manager.get_async_session_context() as session:
        session.add(KnowledgeBase(db_id="kb_test", name="Test KB", kb_type="lightrag"))
        session.add(KnowledgeFile(file_id="file_test", db_id="kb_test", filename="sample.md"))

    compiled = CompiledDocument(
        source_uri="sample.md",
        title="sample.md",
        asset_type="file",
        markdown_content="# Title",
        parser="legacy_markdown",
        parser_version=None,
        status="success",
        content_hash="hash_content",
        ast_hash="hash_ast",
        parse_config={"db_id": "kb_test"},
        parser_trace=[{"parser": "legacy_markdown", "status": "success"}],
        stats={"node_count": 2, "evidence_anchor_count": 2},
        nodes=[
            CompiledNode(key="n0", node_type="heading", node_order=0, text="# Title", char_start=0, char_end=7),
            CompiledNode(
                key="n1",
                node_type="table",
                node_order=1,
                table_json={"rows": [["A", "B"]]},
                text="| A | B |",
            ),
        ],
        evidence_anchors=[
            CompiledEvidenceAnchor(
                node_key="n0",
                anchor_type="text",
                source_uri="sample.md",
                text_excerpt="# Title",
                confidence=1.0,
            ),
            CompiledEvidenceAnchor(
                node_key="n1",
                anchor_type="table",
                source_uri="sample.md",
                text_excerpt="| A | B |",
                confidence=1.0,
            ),
        ],
    )

    result = await KnowledgeObjectRepository().persist_compiled_document(
        db_id="kb_test",
        file_id="file_test",
        compiled=compiled,
        owner="user_test",
    )

    assert result["status"] == "success"
    assert result["node_count"] == 2
    assert result["evidence_anchor_count"] == 2

    async with sqlite_pg_manager.get_async_session_context() as session:
        counts = {}
        for model in (SourceAsset, DocumentVersion, DocumentNode, EvidenceAnchor):
            value = await session.execute(select(func.count()).select_from(model))
            counts[model.__tablename__] = value.scalar_one()

        version_result = await session.execute(
            select(DocumentVersion).where(DocumentVersion.doc_version_id == result["doc_version_id"])
        )
        version = version_result.scalar_one()

    assert counts == {
        "source_assets": 1,
        "document_versions": 1,
        "document_nodes": 2,
        "evidence_anchors": 2,
    }
    assert version.file_id == "file_test"
    assert version.parse_config["parser_trace"][0]["parser"] == "legacy_markdown"


@pytest.mark.asyncio
async def test_repository_persists_failed_document_version(sqlite_pg_manager) -> None:
    async with sqlite_pg_manager.get_async_session_context() as session:
        session.add(KnowledgeBase(db_id="kb_test", name="Test KB", kb_type="lightrag"))

    compiled = CompiledDocument(
        source_uri="broken.pdf",
        title="broken.pdf",
        asset_type="file",
        markdown_content="",
        parser="docling",
        parser_version="2.x",
        status="failed",
        parse_config={"db_id": "kb_test"},
        parser_trace=[{"parser": "docling", "status": "failed", "error": "bad input"}],
        stats={"node_count": 0, "evidence_anchor_count": 0},
        error_message="bad input",
    )

    result = await KnowledgeObjectRepository().persist_compiled_document(
        db_id="kb_test",
        file_id=None,
        compiled=compiled,
    )

    async with sqlite_pg_manager.get_async_session_context() as session:
        version_result = await session.execute(
            select(DocumentVersion).where(DocumentVersion.doc_version_id == result["doc_version_id"])
        )
        version = version_result.scalar_one()
        node_count = (await session.execute(select(func.count()).select_from(DocumentNode))).scalar_one()
        anchor_count = (await session.execute(select(func.count()).select_from(EvidenceAnchor))).scalar_one()

    assert version.status == "failed"
    assert version.error_message == "bad input"
    assert node_count == 0
    assert anchor_count == 0


@pytest.mark.asyncio
async def test_parse_file_persists_compiler_objects_and_legacy_markdown(sqlite_pg_manager, tmp_path: Path) -> None:
    source = tmp_path / "sample.md"
    source.write_text("# Title\n\nEvidence paragraph.", encoding="utf-8")

    async with sqlite_pg_manager.get_async_session_context() as session:
        session.add(KnowledgeBase(db_id="kb_test", name="Test KB", kb_type="dummy"))

    kb = DummyKnowledgeBase(str(tmp_path / "work"))
    kb.databases_meta = {"kb_test": {"metadata": {}}}
    kb.files_meta = {
        "file_test": {
            "file_id": "file_test",
            "database_id": "kb_test",
            "filename": "sample.md",
            "path": str(source),
            "status": FileStatus.UPLOADED,
            "processing_params": {"content_type": "file"},
        }
    }

    async def fake_save_markdown(db_id: str, file_id: str, content: str) -> str:
        assert db_id == "kb_test"
        assert file_id == "file_test"
        assert "# Title" in content
        return "minio://kb-parsed/kb_test/file_test/parsed.md"

    kb._save_markdown_to_minio = fake_save_markdown

    result = await kb.parse_file("kb_test", "file_test", operator_id="user_test")

    assert result["status"] == FileStatus.PARSED
    assert result["markdown_file"] == "minio://kb-parsed/kb_test/file_test/parsed.md"
    assert result["processing_params"]["document_compile"]["status"] == "success"

    async with sqlite_pg_manager.get_async_session_context() as session:
        node_count = (await session.execute(select(func.count()).select_from(DocumentNode))).scalar_one()
        anchor_count = (await session.execute(select(func.count()).select_from(EvidenceAnchor))).scalar_one()
        version = (await session.execute(select(DocumentVersion))).scalar_one()

    assert version.file_id == "file_test"
    assert node_count == 2
    assert anchor_count == 2
