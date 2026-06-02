from __future__ import annotations

from typing import Any

from sqlalchemy import func, select

from src.knowledge.compiler.models import CompiledDocument
from src.storage.postgres.manager import pg_manager
from src.storage.postgres.models_knowledge import DocumentNode, DocumentVersion, EvidenceAnchor, SourceAsset
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

    def _asset_id(self, db_id: str, file_id: str | None, source_uri: str) -> str:
        stable_key = file_id or source_uri
        return f"asset_{hashstr(f'{db_id}:{stable_key}', length=24)}"

    def _doc_version_id(self, asset_id: str, version_index: int, content_hash: str) -> str:
        return f"docv_{hashstr(f'{asset_id}:{version_index}:{content_hash}', length=24)}"

    def _node_id(self, doc_version_id: str, node_key: str, node_order: int) -> str:
        return f"node_{hashstr(f'{doc_version_id}:{node_key}:{node_order}', length=32)}"

    def _evidence_id(self, doc_version_id: str, node_id: str, evidence_index: int) -> str:
        return f"ev_{hashstr(f'{doc_version_id}:{node_id}:{evidence_index}', length=32)}"
