from __future__ import annotations

from pathlib import Path

import pytest

from src.knowledge.compiler.models import CompiledDocument, CompiledEvidenceAnchor, CompiledNode
from src.repositories.knowledge_object_repository import KnowledgeObjectRepository
from src.repositories.wiki_repository import WikiRepository
from src.services.auto_wiki_service import AutoWikiService
from src.storage.postgres.manager import pg_manager
from src.storage.postgres.models_knowledge import KnowledgeBase, KnowledgeFile, WikiPage


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


async def _seed_evidence_bound_chunks(db_id: str = "kb_wiki", file_id: str = "file_wiki") -> None:
    async with pg_manager.get_async_session_context() as session:
        session.add(KnowledgeBase(db_id=db_id, name="Wiki KB", kb_type="milvus"))
        session.add(KnowledgeFile(file_id=file_id, db_id=db_id, filename="retrieval-notes.md"))

    compiled = CompiledDocument(
        source_uri="retrieval-notes.md",
        title="retrieval-notes.md",
        asset_type="file",
        markdown_content="# Retrieval Notes\n\nAutoWiki turns citations into glossary topic pages.",
        parser="legacy_markdown",
        parser_version=None,
        status="success",
        content_hash="hash_wiki_content",
        ast_hash="hash_wiki_ast",
        parse_config={"db_id": db_id},
        parser_trace=[{"parser": "legacy_markdown", "status": "success"}],
        stats={"node_count": 2, "evidence_anchor_count": 2},
        nodes=[
            CompiledNode(key="n0", node_type="heading", node_order=0, text="# Retrieval Notes"),
            CompiledNode(
                key="n1",
                node_type="paragraph",
                node_order=1,
                text="AutoWiki turns citations into glossary topic pages.",
            ),
        ],
        evidence_anchors=[
            CompiledEvidenceAnchor(
                node_key="n0",
                anchor_type="text",
                source_uri="retrieval-notes.md",
                text_excerpt="# Retrieval Notes",
                confidence=1.0,
            ),
            CompiledEvidenceAnchor(
                node_key="n1",
                anchor_type="text",
                source_uri="retrieval-notes.md",
                text_excerpt="AutoWiki turns citations into glossary topic pages.",
                confidence=0.95,
            ),
        ],
    )
    await KnowledgeObjectRepository().persist_compiled_document(db_id, file_id, compiled)
    await KnowledgeObjectRepository().bind_chunks_to_latest_evidence(
        db_id,
        file_id,
        [
            {
                "id": f"{file_id}_chunk_0",
                "chunk_id": f"{file_id}_chunk_0",
                "file_id": file_id,
                "filename": "retrieval-notes.md",
                "source": "retrieval-notes.md",
                "chunk_index": 0,
                "content": "# Retrieval Notes\n\nAutoWiki turns citations into glossary topic pages.",
            }
        ],
    )


@pytest.mark.asyncio
async def test_auto_wiki_rebuild_generates_page_types_and_backlinks(sqlite_pg_manager) -> None:
    await _seed_evidence_bound_chunks()

    result = await AutoWikiService().rebuild_wiki("kb_wiki", max_topics=4)

    assert result["status"] == "success"
    assert result["page_counts"]["home"] == 1
    assert result["page_counts"]["document"] == 1
    assert result["page_counts"]["glossary"] == 1
    assert result["page_counts"]["topic"] >= 1

    pages = await WikiRepository().list_pages("kb_wiki", limit=20)
    page_types = {page["page_type"] for page in pages["items"]}
    assert {"home", "document", "topic", "glossary"}.issubset(page_types)

    document_page = next(page for page in pages["items"] if page["page_type"] == "document")
    full_document_page = await WikiRepository().get_page("kb_wiki", document_page["page_id"])
    assert full_document_page is not None
    assert full_document_page["freshness"]["status"] == "fresh"
    assert len(full_document_page["evidence_ids"]) == 2
    assert full_document_page["outline"]["style"] == "storm-lite"
    assert len(full_document_page["outline"]["perspectives"]) == 3
    assert "## STORM Outline" in full_document_page["markdown"]
    assert full_document_page["review"]["status"] == "pending_review"
    assert full_document_page["evidence_coverage"]["status"] == "covered"
    assert full_document_page["evidence_coverage"]["ratio"] == 1.0
    assert full_document_page["citations"][0]["source"] == "EvidenceAnchor"
    assert full_document_page["claims"][0]["status"] == "supported"
    assert full_document_page["open_questions"]
    assert full_document_page["disputes"][0]["status"] == "none_detected"
    assert full_document_page["rag_role"]["primary"] is False
    assert full_document_page["rag_role"]["role"] == "evidence_candidate_recall"
    assert any(backlink["page_type"] == "home" for backlink in full_document_page["backlinks"])
    assert any(backlink["page_type"] == "glossary" for backlink in full_document_page["backlinks"])


@pytest.mark.asyncio
async def test_auto_wiki_local_rebuild_updates_document_scope(sqlite_pg_manager) -> None:
    await _seed_evidence_bound_chunks()
    await AutoWikiService().rebuild_wiki("kb_wiki", max_topics=4)

    local_result = await AutoWikiService().rebuild_wiki("kb_wiki", file_id="file_wiki")

    assert local_result["scope"] == "file"
    assert local_result["page_counts"] == {"document": 1}

    document_pages = await WikiRepository().list_pages("kb_wiki", page_type="document")
    assert len(document_pages["items"]) == 1
    assert document_pages["items"][0]["source_id"] == "file_wiki"

    async with pg_manager.get_async_session_context() as session:
        rows = await session.execute(WikiPage.__table__.select())
        assert len(rows.all()) >= 4
