from __future__ import annotations

import pytest

from src.services.evidence_service import EvidenceQueryService


class FakeKnowledgeBase:
    async def aquery(self, query_text: str, db_id: str, **kwargs):
        assert query_text == "worldline evidence"
        assert db_id == "kb_test"
        assert kwargs["include_evidence"] is True
        assert kwargs["search_mode"] == "hybrid"
        return [
            {
                "content": "Worldline stores claims with evidence anchors. Extra detail follows.",
                "metadata": {"chunk_id": "chunk_1"},
                "score": 0.82,
            }
        ]


class FakeRepository:
    async def decorate_retrieval_results(self, db_id: str, retrieved_chunks: list[dict]):
        assert db_id == "kb_test"
        chunk = dict(retrieved_chunks[0])
        chunk["metadata"] = {
            **chunk["metadata"],
            "evidence_ids": ["ev_1"],
            "doc_version_id": "docv_1",
        }
        chunk["citations"] = [
            {
                "evidence_id": "ev_1",
                "doc_version_id": "docv_1",
                "node_id": "node_1",
                "source_uri": "sample.md",
                "text_excerpt": "Worldline stores claims with evidence anchors.",
            }
        ]
        return [chunk]


@pytest.mark.asyncio
async def test_evidence_query_service_builds_claims_citations_and_route_trace(monkeypatch) -> None:
    import src

    monkeypatch.setattr(src, "knowledge_base", FakeKnowledgeBase())

    response = await EvidenceQueryService(repository=FakeRepository()).query_with_evidence(
        "kb_test",
        "worldline evidence",
        meta={"final_top_k": 3},
    )

    assert response["status"] == "success"
    assert response["claims"][0]["evidence_ids"] == ["ev_1"]
    assert response["claims"][0]["confidence"] == 0.82
    assert response["citations"][0]["evidence_id"] == "ev_1"
    assert response["route_trace"]["dense"] is True
    assert response["route_trace"]["sparse"] is True
    assert response["route_trace"]["bm25"] is True
    assert response["route_trace"]["channels"] == ["dense", "sparse_keyword"]
    assert response["route_trace"]["sparse_strategy"] == "keyword_bm25_proxy"
    assert response["route_trace"]["evidence_enriched"] is True
    assert response["retrieved_chunks"][0]["metadata"]["doc_version_id"] == "docv_1"


def test_evidence_query_service_extracts_lightrag_style_chunks() -> None:
    raw_result = {
        "data": {
            "chunks": [
                {"content": "chunk one", "metadata": {"chunk_id": "c1"}},
                "invalid",
            ]
        }
    }

    chunks = EvidenceQueryService(repository=FakeRepository())._extract_retrieved_chunks(raw_result)

    assert chunks == [{"content": "chunk one", "metadata": {"chunk_id": "c1"}}]


def test_phase3_embedding_and_reranker_candidates_include_qwen_and_bge() -> None:
    from src.config.static.models import DEFAULT_EMBED_MODELS, DEFAULT_RERANKERS

    assert "siliconflow/Qwen/Qwen3-Embedding-0.6B" in DEFAULT_EMBED_MODELS
    assert "siliconflow/BAAI/bge-m3" in DEFAULT_EMBED_MODELS
    assert "siliconflow/BAAI/bge-reranker-v2-m3" in DEFAULT_RERANKERS
    assert "dashscope/qwen3-rerank" in DEFAULT_RERANKERS
