from __future__ import annotations

from typing import Any

from sqlalchemy import delete, desc, func, select

from src.knowledge.compiler.models import CompiledDocument
from src.storage.postgres.manager import pg_manager
from src.storage.postgres.models_knowledge import (
    DocumentNode,
    DocumentVersion,
    EvidenceAnchor,
    KnowledgeChunk,
    SourceAsset,
)
from src.utils import hashstr


class KnowledgeObjectRepository:
    """Persistence boundary for Phase 2 compiled knowledge objects."""

    async def persist_compiled_document(
        self,
        db_id: str,
        file_id: str | None,
        compiled: CompiledDocument,
        owner: str | None = None,
    ) -> dict[str, Any]:
        asset_id = self._asset_id(db_id, file_id, compiled.source_uri)

        async with pg_manager.get_async_session_context() as session:
            result = await session.execute(select(SourceAsset).where(SourceAsset.asset_id == asset_id))
            source_asset = result.scalar_one_or_none()
            asset_payload = {
                "db_id": db_id,
                "asset_type": compiled.asset_type,
                "uri": compiled.source_uri,
                "title": compiled.title,
                "content_hash": compiled.content_hash,
                "owner": owner,
                "status": "active" if compiled.status == "success" else "error",
                "asset_metadata": {
                    "file_id": file_id,
                    "parser": compiled.parser,
                    "parser_trace": compiled.parser_trace,
                },
            }
            if source_asset is None:
                source_asset = SourceAsset(asset_id=asset_id, **asset_payload)
                session.add(source_asset)
            else:
                for key, value in asset_payload.items():
                    setattr(source_asset, key, value)
            await session.flush()

            max_version_result = await session.execute(
                select(func.max(DocumentVersion.version_index)).where(DocumentVersion.asset_id == asset_id)
            )
            version_index = int(max_version_result.scalar() or 0) + 1
            doc_version_id = self._doc_version_id(asset_id, version_index, compiled.content_hash or compiled.status)

            document_version = DocumentVersion(
                doc_version_id=doc_version_id,
                asset_id=asset_id,
                file_id=file_id,
                parser=compiled.parser,
                parser_version=compiled.parser_version,
                status=compiled.status,
                ast_hash=compiled.ast_hash,
                content_hash=compiled.content_hash,
                version_index=version_index,
                parse_config={
                    **compiled.parse_config,
                    "parser_trace": compiled.parser_trace,
                },
                stats=compiled.stats,
                error_message=compiled.error_message,
            )
            session.add(document_version)
            await session.flush()

            node_ids: dict[str, str] = {}
            for node in compiled.nodes:
                node_ids[node.key] = self._node_id(doc_version_id, node.key, node.node_order)

            for node in compiled.nodes:
                session.add(
                    DocumentNode(
                        node_id=node_ids[node.key],
                        doc_version_id=doc_version_id,
                        parent_id=node_ids.get(node.parent_key) if node.parent_key else None,
                        node_type=node.node_type,
                        node_order=node.node_order,
                        text=node.text,
                        table_json=node.table_json,
                        image_ref=node.image_ref,
                        page_start=node.page_start,
                        page_end=node.page_end,
                        bbox=node.bbox,
                        char_start=node.char_start,
                        char_end=node.char_end,
                        node_metadata=node.metadata,
                    )
                )

            evidence_count = 0
            for anchor in compiled.evidence_anchors:
                node_id = node_ids.get(anchor.node_key)
                if not node_id:
                    continue
                evidence_count += 1
                session.add(
                    EvidenceAnchor(
                        evidence_id=self._evidence_id(doc_version_id, node_id, evidence_count),
                        doc_version_id=doc_version_id,
                        node_id=node_id,
                        anchor_type=anchor.anchor_type,
                        source_uri=anchor.source_uri,
                        page=anchor.page,
                        line_start=anchor.line_start,
                        line_end=anchor.line_end,
                        bbox=anchor.bbox,
                        char_start=anchor.char_start,
                        char_end=anchor.char_end,
                        text_span=anchor.text_span,
                        text_excerpt=anchor.text_excerpt,
                        confidence=anchor.confidence,
                        evidence_metadata=anchor.metadata,
                    )
                )

        return {
            "asset_id": asset_id,
            "doc_version_id": doc_version_id,
            "version_index": version_index,
            "status": compiled.status,
            "node_count": len(compiled.nodes),
            "evidence_anchor_count": evidence_count,
            "parser": compiled.parser,
            "ast_hash": compiled.ast_hash,
            "content_hash": compiled.content_hash,
        }

    async def bind_chunks_to_latest_evidence(
        self,
        db_id: str,
        file_id: str,
        chunks: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Persist chunk-to-evidence bindings and return chunks enriched with evidence metadata."""

        if not chunks:
            return chunks

        async with pg_manager.get_async_session_context() as session:
            version = await self._get_latest_successful_version(session, db_id=db_id, file_id=file_id)
            if version is None:
                return chunks

            anchors = await self._get_anchors_for_version(session, version.doc_version_id)
            enriched_chunks = self._assign_evidence_ids_to_chunks(chunks, anchors, version.doc_version_id)

            await session.execute(
                delete(KnowledgeChunk).where(KnowledgeChunk.db_id == db_id, KnowledgeChunk.file_id == file_id)
            )
            for chunk in enriched_chunks:
                metadata = dict(chunk.get("metadata") or {})
                metadata.update(
                    {
                        "filename": chunk.get("filename"),
                        "source": chunk.get("source"),
                        "doc_version_id": version.doc_version_id,
                    }
                )
                session.add(
                    KnowledgeChunk(
                        chunk_id=str(chunk.get("chunk_id") or chunk.get("id")),
                        db_id=db_id,
                        file_id=file_id,
                        doc_version_id=version.doc_version_id,
                        chunk_index=int(chunk.get("chunk_index") or 0),
                        text=str(chunk.get("content") or ""),
                        contextual_text=chunk.get("contextual_text"),
                        evidence_ids=metadata.get("evidence_ids") or [],
                        dense_vector_ref=chunk.get("id"),
                        sparse_vector_ref=metadata.get("sparse_vector_ref"),
                        chunk_metadata=metadata,
                    )
                )

        return enriched_chunks

    async def decorate_retrieval_results(
        self,
        db_id: str,
        retrieved_chunks: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Attach persisted evidence ids and citation summaries to retrieval results."""

        if not retrieved_chunks:
            return retrieved_chunks

        chunk_ids = [
            str(chunk.get("metadata", {}).get("chunk_id") or chunk.get("chunk_id") or "")
            for chunk in retrieved_chunks
        ]
        chunk_ids = [chunk_id for chunk_id in chunk_ids if chunk_id]
        if not chunk_ids:
            return retrieved_chunks

        async with pg_manager.get_async_session_context() as session:
            chunk_result = await session.execute(
                select(KnowledgeChunk).where(KnowledgeChunk.db_id == db_id, KnowledgeChunk.chunk_id.in_(chunk_ids))
            )
            persisted_chunks = {chunk.chunk_id: chunk for chunk in chunk_result.scalars().all()}

            evidence_ids: list[str] = []
            for chunk in persisted_chunks.values():
                for evidence_id in chunk.evidence_ids or []:
                    if evidence_id not in evidence_ids:
                        evidence_ids.append(evidence_id)

            citations_by_id = {}
            if evidence_ids:
                citation_result = await session.execute(
                    select(EvidenceAnchor, DocumentNode, DocumentVersion, SourceAsset)
                    .join(DocumentNode, EvidenceAnchor.node_id == DocumentNode.node_id)
                    .join(DocumentVersion, EvidenceAnchor.doc_version_id == DocumentVersion.doc_version_id)
                    .join(SourceAsset, DocumentVersion.asset_id == SourceAsset.asset_id)
                    .where(SourceAsset.db_id == db_id, EvidenceAnchor.evidence_id.in_(evidence_ids))
                )
                for anchor, node, version, asset in citation_result.all():
                    citations_by_id[anchor.evidence_id] = self._serialize_evidence(anchor, node, version, asset)

        enriched: list[dict[str, Any]] = []
        for chunk in retrieved_chunks:
            chunk_id = str(chunk.get("metadata", {}).get("chunk_id") or chunk.get("chunk_id") or "")
            persisted = persisted_chunks.get(chunk_id)
            if persisted is None:
                enriched.append(chunk)
                continue

            metadata = dict(chunk.get("metadata") or {})
            evidence_ids = list(persisted.evidence_ids or [])
            metadata["evidence_ids"] = evidence_ids
            metadata["doc_version_id"] = persisted.doc_version_id
            metadata["chunk_index"] = persisted.chunk_index
            metadata.setdefault("file_id", persisted.file_id)

            enriched_chunk = dict(chunk)
            enriched_chunk["metadata"] = metadata
            enriched_chunk["citations"] = [citations_by_id[eid] for eid in evidence_ids if eid in citations_by_id]
            enriched.append(enriched_chunk)

        return enriched

    async def list_evidence_anchors(
        self,
        db_id: str,
        *,
        file_id: str | None = None,
        doc_version_id: str | None = None,
        evidence_ids: list[str] | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        limit = max(1, min(int(limit or 50), 200))
        offset = max(0, int(offset or 0))

        async with pg_manager.get_async_session_context() as session:
            stmt = (
                select(EvidenceAnchor, DocumentNode, DocumentVersion, SourceAsset)
                .join(DocumentNode, EvidenceAnchor.node_id == DocumentNode.node_id)
                .join(DocumentVersion, EvidenceAnchor.doc_version_id == DocumentVersion.doc_version_id)
                .join(SourceAsset, DocumentVersion.asset_id == SourceAsset.asset_id)
                .where(SourceAsset.db_id == db_id)
                .order_by(EvidenceAnchor.created_at.desc(), EvidenceAnchor.id.desc())
                .offset(offset)
                .limit(limit + 1)
            )
            if file_id:
                stmt = stmt.where(DocumentVersion.file_id == file_id)
            if doc_version_id:
                stmt = stmt.where(EvidenceAnchor.doc_version_id == doc_version_id)
            if evidence_ids:
                stmt = stmt.where(EvidenceAnchor.evidence_id.in_(evidence_ids))

            rows = (await session.execute(stmt)).all()

        has_more = len(rows) > limit
        items = [
            self._serialize_evidence(anchor, node, version, asset)
            for anchor, node, version, asset in rows[:limit]
        ]
        return {
            "items": items,
            "limit": limit,
            "offset": offset,
            "has_more": has_more,
        }

    async def get_evidence_anchor(self, db_id: str, evidence_id: str) -> dict[str, Any] | None:
        result = await self.list_evidence_anchors(db_id, evidence_ids=[evidence_id], limit=1)
        return result["items"][0] if result["items"] else None

    async def list_chunks(
        self,
        db_id: str,
        *,
        file_id: str | None = None,
        doc_version_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        limit = max(1, min(int(limit or 50), 200))
        offset = max(0, int(offset or 0))

        async with pg_manager.get_async_session_context() as session:
            stmt = (
                select(KnowledgeChunk)
                .where(KnowledgeChunk.db_id == db_id)
                .order_by(KnowledgeChunk.file_id, KnowledgeChunk.chunk_index)
                .offset(offset)
                .limit(limit + 1)
            )
            if file_id:
                stmt = stmt.where(KnowledgeChunk.file_id == file_id)
            if doc_version_id:
                stmt = stmt.where(KnowledgeChunk.doc_version_id == doc_version_id)

            rows = (await session.execute(stmt)).scalars().all()

        has_more = len(rows) > limit
        items = [self._serialize_chunk(chunk) for chunk in rows[:limit]]
        return {
            "items": items,
            "limit": limit,
            "offset": offset,
            "has_more": has_more,
        }

    def _asset_id(self, db_id: str, file_id: str | None, source_uri: str) -> str:
        stable_key = file_id or source_uri
        return f"asset_{hashstr(f'{db_id}:{stable_key}', length=24)}"

    def _doc_version_id(self, asset_id: str, version_index: int, content_hash: str) -> str:
        return f"docv_{hashstr(f'{asset_id}:{version_index}:{content_hash}', length=24)}"

    def _node_id(self, doc_version_id: str, node_key: str, node_order: int) -> str:
        return f"node_{hashstr(f'{doc_version_id}:{node_key}:{node_order}', length=32)}"

    def _evidence_id(self, doc_version_id: str, node_id: str, evidence_index: int) -> str:
        return f"ev_{hashstr(f'{doc_version_id}:{node_id}:{evidence_index}', length=32)}"

    async def _get_latest_successful_version(self, session, *, db_id: str, file_id: str) -> DocumentVersion | None:
        result = await session.execute(
            select(DocumentVersion)
            .join(SourceAsset, DocumentVersion.asset_id == SourceAsset.asset_id)
            .where(
                SourceAsset.db_id == db_id,
                DocumentVersion.file_id == file_id,
                DocumentVersion.status == "success",
            )
            .order_by(desc(DocumentVersion.version_index), desc(DocumentVersion.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def _get_anchors_for_version(self, session, doc_version_id: str) -> list[EvidenceAnchor]:
        result = await session.execute(
            select(EvidenceAnchor)
            .where(EvidenceAnchor.doc_version_id == doc_version_id)
            .order_by(EvidenceAnchor.page, EvidenceAnchor.line_start, EvidenceAnchor.char_start, EvidenceAnchor.id)
        )
        return list(result.scalars().all())

    def _assign_evidence_ids_to_chunks(
        self,
        chunks: list[dict[str, Any]],
        anchors: list[EvidenceAnchor],
        doc_version_id: str,
    ) -> list[dict[str, Any]]:
        if not anchors:
            return chunks

        enriched: list[dict[str, Any]] = []
        for idx, chunk in enumerate(chunks):
            content = str(chunk.get("content") or "")
            evidence_ids = [
                anchor.evidence_id
                for anchor in anchors
                if self._chunk_contains_anchor(content, str(anchor.text_excerpt or ""))
            ]
            if not evidence_ids:
                fallback_anchor = anchors[min(idx, len(anchors) - 1)]
                evidence_ids = [fallback_anchor.evidence_id]

            metadata = dict(chunk.get("metadata") or {})
            metadata["evidence_ids"] = evidence_ids
            metadata["doc_version_id"] = doc_version_id

            enriched_chunk = dict(chunk)
            enriched_chunk["metadata"] = metadata
            enriched.append(enriched_chunk)

        return enriched

    def _chunk_contains_anchor(self, chunk_text: str, anchor_text: str) -> bool:
        normalized_chunk = " ".join((chunk_text or "").split()).lower()
        normalized_anchor = " ".join((anchor_text or "").split()).lower()
        if not normalized_chunk or not normalized_anchor:
            return False
        if len(normalized_anchor) <= 200:
            return normalized_anchor in normalized_chunk
        return normalized_anchor[:200] in normalized_chunk

    def _serialize_evidence(
        self,
        anchor: EvidenceAnchor,
        node: DocumentNode,
        version: DocumentVersion,
        asset: SourceAsset,
    ) -> dict[str, Any]:
        return {
            "evidence_id": anchor.evidence_id,
            "doc_version_id": anchor.doc_version_id,
            "node_id": anchor.node_id,
            "asset_id": version.asset_id,
            "file_id": version.file_id,
            "source_uri": anchor.source_uri,
            "source_title": asset.title,
            "anchor_type": anchor.anchor_type,
            "page": anchor.page,
            "line_start": anchor.line_start,
            "line_end": anchor.line_end,
            "bbox": anchor.bbox,
            "char_start": anchor.char_start,
            "char_end": anchor.char_end,
            "text_excerpt": self._trim_text(anchor.text_excerpt, 500),
            "confidence": anchor.confidence,
            "metadata": anchor.evidence_metadata or {},
            "node": {
                "node_type": node.node_type,
                "node_order": node.node_order,
                "text": self._trim_text(node.text, 500),
                "metadata": node.node_metadata or {},
            },
        }

    def _serialize_chunk(self, chunk: KnowledgeChunk) -> dict[str, Any]:
        return {
            "chunk_id": chunk.chunk_id,
            "db_id": chunk.db_id,
            "file_id": chunk.file_id,
            "doc_version_id": chunk.doc_version_id,
            "chunk_index": chunk.chunk_index,
            "text": self._trim_text(chunk.text, 1000),
            "contextual_text": self._trim_text(chunk.contextual_text, 1000),
            "evidence_ids": chunk.evidence_ids or [],
            "metadata": chunk.chunk_metadata or {},
        }

    def _trim_text(self, value: str | None, limit: int) -> str | None:
        if value is None:
            return None
        text = str(value)
        if len(text) <= limit:
            return text
        return f"{text[:limit].rstrip()}..."
