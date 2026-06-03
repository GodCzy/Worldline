from __future__ import annotations

import json
import hashlib
import os
import tempfile
import time
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import aiofiles

from src.knowledge.compiler.models import CompiledDocument, CompiledEvidenceAnchor, CompiledNode
from src.utils import hashstr, logger


class DocumentCompileError(Exception):
    """Raised when a document cannot be compiled into an AST."""


def _is_minio_url(file_path: str) -> bool:
    return file_path.startswith(("http://", "https://", "s3://", "minio://")) or "minio" in file_path.lower()


def _parse_minio_url(file_path: str) -> tuple[str, str]:
    parsed = urlparse(file_path)
    if parsed.scheme == "minio":
        return parsed.netloc, parsed.path.lstrip("/")

    object_name = parsed.path.lstrip("/")
    path_parts = object_name.split("/", 1)
    if len(path_parts) > 1:
        return path_parts[0], path_parts[1]
    raise ValueError(f"无法解析MinIO URL中的bucket名称: {file_path}")


def _process_ocr_file(processor_type: str, file_path: str, params: dict[str, Any] | None = None) -> str:
    from src.plugins.document_processor_factory import DocumentProcessorFactory

    return DocumentProcessorFactory.process_file(processor_type, file_path, params)


def _get_docling_converter() -> Any:
    from src.knowledge.indexing import _get_docling_converter as get_converter

    return get_converter()


def _convert_with_docling(file_path: Path, params: dict[str, Any]) -> str:
    from src.knowledge.indexing import _convert_with_docling as convert

    return convert(file_path, params)


async def _process_file_to_markdown(file_path: str, params: dict[str, Any] | None = None) -> str:
    from src.knowledge.indexing import process_file_to_markdown

    return await process_file_to_markdown(file_path, params=params)


async def _process_url_to_markdown(url: str, params: dict[str, Any] | None = None) -> str:
    from src.knowledge.indexing import process_url_to_markdown

    return await process_url_to_markdown(url, params=params)


class DocumentCompiler:
    """Compile source documents into Markdown, Document AST nodes, and evidence anchors."""

    DOCLING_EXTENSIONS = {".pdf", ".docx", ".pptx", ".xlsx", ".html", ".htm"}
    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}
    OCR_FALLBACKS = ("onnx_rapid_ocr", "mineru_ocr", "mineru_official", "paddlex_ocr")
    OCR_PROCESSOR_TYPES = {
        "onnx_rapid_ocr",
        "mineru_ocr",
        "mineru_official",
        "paddlex_ocr",
        "deepseek_ocr",
    }

    async def compile_url(self, url: str, params: dict[str, Any] | None = None) -> CompiledDocument:
        params = dict(params or {})
        parser_trace: list[dict[str, Any]] = []
        started = time.time()
        try:
            markdown = await _process_url_to_markdown(url, params=params)
            parser_trace.append({"parser": "url_markdown", "status": "success"})
            return await self._build_markdown_document(
                markdown_content=markdown,
                source_uri=url,
                title=url,
                asset_type="url",
                parser="url_markdown",
                parser_version=None,
                parser_trace=parser_trace,
                parse_config=params,
                started=started,
            )
        except Exception as exc:  # noqa: BLE001
            parser_trace.append({"parser": "url_markdown", "status": "failed", "error": str(exc)})
            return await self._failed_document(
                source_uri=url,
                title=url,
                asset_type="url",
                parser="url_markdown",
                parser_trace=parser_trace,
                parse_config=params,
                error=exc,
                started=started,
            )

    async def compile_file(self, file_path: str, params: dict[str, Any] | None = None) -> CompiledDocument:
        params = dict(params or {})
        source_uri = file_path
        parser_trace: list[dict[str, Any]] = []
        started = time.time()

        async with self._materialized_source(file_path) as actual_path:
            path = Path(actual_path)
            suffix = path.suffix.lower()
            title = path.name

            try:
                if suffix in self.DOCLING_EXTENSIONS:
                    return await self._compile_with_docling(path, source_uri, title, params, parser_trace, started)

                if suffix in self.IMAGE_EXTENSIONS:
                    return await self._compile_with_ocr_fallbacks(
                        path,
                        source_uri,
                        title,
                        params,
                        parser_trace,
                        started,
                    )

                if suffix in {".md", ".txt"}:
                    markdown = await self._read_plain_text(path)
                else:
                    markdown = await _process_file_to_markdown(str(path), params=params)
                parser_trace.append({"parser": "legacy_markdown", "status": "success"})
                return await self._build_markdown_document(
                    markdown_content=markdown,
                    source_uri=source_uri,
                    title=title,
                    asset_type=self._asset_type_for_suffix(suffix),
                    parser="legacy_markdown",
                    parser_version=None,
                    parser_trace=parser_trace,
                    parse_config=params,
                    started=started,
                )
            except Exception as exc:  # noqa: BLE001
                parser_trace.append({"parser": "document_compiler", "status": "failed", "error": str(exc)})
                return await self._failed_document(
                    source_uri=source_uri,
                    title=title,
                    asset_type=self._asset_type_for_suffix(suffix),
                    parser="document_compiler",
                    parser_trace=parser_trace,
                    parse_config=params,
                    error=exc,
                    started=started,
                )

    async def _compile_with_docling(
        self,
        path: Path,
        source_uri: str,
        title: str,
        params: dict[str, Any],
        parser_trace: list[dict[str, Any]],
        started: float,
    ) -> CompiledDocument:
        try:
            converter = _get_docling_converter()
            result = await self._to_thread(converter.convert, path)
            status_name = getattr(getattr(result, "status", None), "name", str(getattr(result, "status", "")))
            if status_name and status_name != "SUCCESS":
                raise DocumentCompileError(f"Docling 转换失败: {status_name}")

            doc = getattr(result, "document", None)
            markdown = await self._to_thread(_convert_with_docling, path, params)
            parser_trace.append({"parser": "docling", "status": "success"})
            nodes = self._nodes_from_docling_document(doc, markdown)
            if not nodes:
                nodes = self._nodes_from_markdown(markdown)

            return await self._build_document(
                markdown_content=markdown,
                source_uri=source_uri,
                title=title,
                asset_type=self._asset_type_for_suffix(path.suffix.lower()),
                parser="docling",
                parser_version=self._docling_version(),
                parser_trace=parser_trace,
                parse_config=params,
                nodes=nodes,
                started=started,
            )
        except Exception as exc:  # noqa: BLE001
            parser_trace.append({"parser": "docling", "status": "failed", "error": str(exc)})
            if path.suffix.lower() in {".pdf"} | self.IMAGE_EXTENSIONS:
                return await self._compile_with_ocr_fallbacks(path, source_uri, title, params, parser_trace, started)

            try:
                markdown = await _process_file_to_markdown(str(path), params=params)
                parser_trace.append({"parser": "legacy_markdown", "status": "success"})
                return await self._build_markdown_document(
                    markdown_content=markdown,
                    source_uri=source_uri,
                    title=title,
                    asset_type=self._asset_type_for_suffix(path.suffix.lower()),
                    parser="legacy_markdown",
                    parser_version=None,
                    parser_trace=parser_trace,
                    parse_config=params,
                    started=started,
                )
            except Exception as legacy_exc:  # noqa: BLE001
                parser_trace.append({"parser": "legacy_markdown", "status": "failed", "error": str(legacy_exc)})
                raise legacy_exc from exc

    async def _compile_with_ocr_fallbacks(
        self,
        path: Path,
        source_uri: str,
        title: str,
        params: dict[str, Any],
        parser_trace: list[dict[str, Any]],
        started: float,
    ) -> CompiledDocument:
        fallbacks = self._resolve_ocr_fallbacks(params)
        last_error: Exception | None = None
        for fallback in fallbacks:
            try:
                text = await self._to_thread(_process_ocr_file, fallback, str(path), params)
                if not text or not text.strip():
                    raise DocumentCompileError(f"{fallback} 未返回可用文本")
                parser_trace.append({"parser": fallback, "status": "success"})
                return await self._build_markdown_document(
                    markdown_content=text,
                    source_uri=source_uri,
                    title=title,
                    asset_type=self._asset_type_for_suffix(path.suffix.lower()),
                    parser=fallback,
                    parser_version=None,
                    parser_trace=parser_trace,
                    parse_config=params,
                    started=started,
                )
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                parser_trace.append({"parser": fallback, "status": "failed", "error": str(exc)})

        try:
            markdown = await _process_file_to_markdown(str(path), params=params)
            parser_trace.append({"parser": "legacy_markdown", "status": "success"})
            return await self._build_markdown_document(
                markdown_content=markdown,
                source_uri=source_uri,
                title=title,
                asset_type=self._asset_type_for_suffix(path.suffix.lower()),
                parser="legacy_markdown",
                parser_version=None,
                parser_trace=parser_trace,
                parse_config=params,
                started=started,
            )
        except Exception as legacy_exc:  # noqa: BLE001
            parser_trace.append({"parser": "legacy_markdown", "status": "failed", "error": str(legacy_exc)})
            raise legacy_exc from last_error

    async def _build_markdown_document(
        self,
        markdown_content: str,
        source_uri: str,
        title: str | None,
        asset_type: str,
        parser: str,
        parser_version: str | None,
        parser_trace: list[dict[str, Any]],
        parse_config: dict[str, Any],
        started: float,
    ) -> CompiledDocument:
        return await self._build_document(
            markdown_content=markdown_content,
            source_uri=source_uri,
            title=title,
            asset_type=asset_type,
            parser=parser,
            parser_version=parser_version,
            parser_trace=parser_trace,
            parse_config=parse_config,
            nodes=self._nodes_from_markdown(markdown_content),
            started=started,
        )

    async def _build_document(
        self,
        markdown_content: str,
        source_uri: str,
        title: str | None,
        asset_type: str,
        parser: str,
        parser_version: str | None,
        parser_trace: list[dict[str, Any]],
        parse_config: dict[str, Any],
        nodes: list[CompiledNode],
        started: float,
    ) -> CompiledDocument:
        content_hash = self._content_hash(markdown_content)
        normalized_nodes = self._normalize_nodes(nodes)
        anchors = self._anchors_from_nodes(normalized_nodes, source_uri)
        ast_hash = self._ast_hash(normalized_nodes)
        stats = self._build_stats(
            markdown_content=markdown_content,
            nodes=normalized_nodes,
            anchors=anchors,
            parser=parser,
            parser_trace=parser_trace,
            started=started,
        )
        return CompiledDocument(
            source_uri=source_uri,
            title=title,
            asset_type=asset_type,
            markdown_content=markdown_content,
            parser=parser,
            parser_version=parser_version,
            status="success",
            content_hash=content_hash,
            ast_hash=ast_hash,
            parse_config=parse_config,
            parser_trace=parser_trace,
            stats=stats,
            nodes=normalized_nodes,
            evidence_anchors=anchors,
        )

    async def _failed_document(
        self,
        source_uri: str,
        title: str | None,
        asset_type: str,
        parser: str,
        parser_trace: list[dict[str, Any]],
        parse_config: dict[str, Any],
        error: Exception,
        started: float,
    ) -> CompiledDocument:
        return CompiledDocument(
            source_uri=source_uri,
            title=title,
            asset_type=asset_type,
            markdown_content="",
            parser=parser,
            parser_version=self._docling_version() if parser == "docling" else None,
            status="failed",
            parse_config=parse_config,
            parser_trace=parser_trace,
            stats={
                "duration_ms": int((time.time() - started) * 1000),
                "node_count": 0,
                "evidence_anchor_count": 0,
                "parser": parser,
                "parser_trace_count": len(parser_trace),
                "parser_success_count": sum(1 for item in parser_trace if item.get("status") == "success"),
                "parser_failure_count": sum(1 for item in parser_trace if item.get("status") == "failed"),
                "fallback_used": self._fallback_used(parser_trace),
            },
            error_message=str(error),
        )

    def _nodes_from_docling_document(self, doc: Any, markdown: str) -> list[CompiledNode]:
        if doc is None:
            return []

        nodes: list[CompiledNode] = []
        cursor = 0

        for item_kind, item in self._docling_ordered_items(doc):
            if item_kind == "table":
                text = self._extract_markdown(item) or self._extract_text(item)
                table_json = self._to_jsonable(getattr(item, "data", None) or getattr(item, "table", None))
                image_ref = None
            elif item_kind == "image":
                image_ref = self._extract_image_ref(item)
                text = self._extract_text(item) or image_ref
                table_json = None
            else:
                text = self._extract_text(item)
                table_json = None
                image_ref = None

            if not text and table_json is None and not image_ref:
                continue

            span_text = image_ref if item_kind == "image" and image_ref else (text or image_ref)
            char_start, char_end, cursor = self._find_text_span(markdown, span_text, cursor)
            line_start, line_end = self._line_range_for_span(markdown, char_start, char_end)
            page_start, page_end = self._extract_page_range(item)
            nodes.append(
                CompiledNode(
                    key=f"n{len(nodes)}",
                    node_type=self._node_type_from_docling(item, item_kind),
                    node_order=len(nodes),
                    text=text,
                    table_json=table_json,
                    image_ref=image_ref,
                    page_start=page_start,
                    page_end=page_end,
                    bbox=self._extract_bbox(item),
                    line_start=line_start,
                    line_end=line_end,
                    char_start=char_start,
                    char_end=char_end,
                    metadata={
                        "source": f"docling.{item_kind}",
                        "docling_label": str(getattr(item, "label", "") or item_kind),
                        "line_start": line_start,
                        "line_end": line_end,
                        "provenance": self._to_jsonable(getattr(item, "prov", None)),
                    },
                )
            )

        return nodes

    def _nodes_from_markdown(self, markdown: str) -> list[CompiledNode]:
        blocks = self._split_markdown_blocks(markdown)
        nodes: list[CompiledNode] = []
        cursor = 0
        for block in blocks:
            char_start = markdown.find(block, cursor)
            if char_start < 0:
                char_start = cursor
            char_end = char_start + len(block)
            line_start, line_end = self._line_range_for_span(markdown, char_start, char_end)
            cursor = max(cursor, char_end)
            node_type = self._classify_markdown_block(block)
            nodes.append(
                CompiledNode(
                    key=f"n{len(nodes)}",
                    node_type=node_type,
                    node_order=len(nodes),
                    text=block,
                    table_json=self._markdown_table_to_json(block) if node_type == "table" else None,
                    image_ref=self._markdown_image_ref(block) if node_type == "image" else None,
                    line_start=line_start,
                    line_end=line_end,
                    char_start=char_start,
                    char_end=char_end,
                    metadata={"source": "markdown", "line_start": line_start, "line_end": line_end},
                )
            )
        return nodes

    def _normalize_nodes(self, nodes: list[CompiledNode]) -> list[CompiledNode]:
        normalized: list[CompiledNode] = []
        for idx, node in enumerate(nodes):
            if not node.text and node.table_json is None and not node.image_ref:
                continue
            node.node_order = idx
            if not node.key:
                node.key = f"n{idx}"
            normalized.append(node)
        return normalized

    def _anchors_from_nodes(self, nodes: list[CompiledNode], source_uri: str) -> list[CompiledEvidenceAnchor]:
        anchors: list[CompiledEvidenceAnchor] = []
        for node in nodes:
            excerpt = (node.text or node.image_ref or "")[:500]
            if not excerpt and node.table_json is None:
                continue
            anchors.append(
                CompiledEvidenceAnchor(
                    node_key=node.key,
                    anchor_type="table" if node.table_json is not None else ("image" if node.image_ref else "text"),
                    source_uri=source_uri,
                    page=node.page_start,
                    line_start=node.line_start,
                    line_end=node.line_end,
                    bbox=node.bbox,
                    char_start=node.char_start,
                    char_end=node.char_end,
                    text_span={"start": node.char_start, "end": node.char_end}
                    if node.char_start is not None and node.char_end is not None
                    else None,
                    text_excerpt=excerpt,
                    confidence=1.0,
                    metadata={"node_order": node.node_order, "node_type": node.node_type},
                )
            )
        return anchors

    def _split_markdown_blocks(self, markdown: str) -> list[str]:
        blocks: list[str] = []
        current: list[str] = []
        for line in markdown.splitlines():
            if line.strip():
                current.append(line)
                continue
            if current:
                blocks.append("\n".join(current).strip())
                current = []
        if current:
            blocks.append("\n".join(current).strip())
        return [block for block in blocks if block]

    def _classify_markdown_block(self, block: str) -> str:
        stripped = block.strip()
        if stripped.startswith("#"):
            return "heading"
        if stripped.startswith("![") and "](" in stripped:
            return "image"
        lines = [line for line in stripped.splitlines() if line.strip()]
        separator = lines[1].replace("|", "").replace(" ", "").strip() if len(lines) >= 2 else ""
        if len(lines) >= 2 and "|" in lines[0] and separator and set(separator) <= {"-", ":"}:
            return "table"
        return "paragraph"

    def _markdown_table_to_json(self, block: str) -> dict[str, Any]:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        rows: list[list[str]] = []
        for line in lines:
            if "|" not in line:
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if cells and not all(set(cell) <= {"-", ":"} for cell in cells):
                rows.append(cells)
        return {"rows": rows}

    def _markdown_image_ref(self, block: str) -> str | None:
        start = block.find("](")
        if start < 0:
            return None
        end = block.find(")", start + 2)
        if end < 0:
            return None
        return block[start + 2 : end]

    def _iter_items(self, value: Any) -> list[Any]:
        if value is None:
            return []
        if isinstance(value, dict):
            return list(value.values())
        return list(value)

    def _docling_ordered_items(self, doc: Any) -> list[tuple[str, Any]]:
        iterator = getattr(doc, "iterate_items", None)
        if callable(iterator):
            ordered: list[tuple[str, Any]] = []
            try:
                for entry in iterator():
                    item = entry[0] if isinstance(entry, tuple) else entry
                    item_kind = self._docling_item_kind(item)
                    if item_kind:
                        ordered.append((item_kind, item))
            except Exception:  # noqa: BLE001
                ordered = []
            if ordered:
                return ordered

        items: list[tuple[str, Any]] = []
        items.extend(("text", item) for item in self._iter_items(getattr(doc, "texts", None)))
        items.extend(("table", item) for item in self._iter_items(getattr(doc, "tables", None)))
        items.extend(("image", item) for item in self._iter_items(getattr(doc, "pictures", None)))
        return items

    def _docling_item_kind(self, item: Any) -> str | None:
        type_name = type(item).__name__.lower()
        label = str(getattr(item, "label", "") or "").lower()
        if "table" in type_name or "table" in label or hasattr(item, "table"):
            return "table"
        if "picture" in type_name or "image" in type_name or hasattr(item, "image"):
            return "image"
        if self._extract_text(item):
            return "text"
        if hasattr(item, "data") and callable(getattr(item, "export_to_markdown", None)):
            return "table"
        return None

    def _node_type_from_docling(self, item: Any, item_kind: str) -> str:
        if item_kind in {"table", "image"}:
            return item_kind
        label = str(getattr(item, "label", None) or "text").lower()
        if "heading" in label or "title" in label:
            return "heading"
        if label in {"paragraph", "section_header", "list_item", "text"}:
            return label
        return "text"

    def _extract_text(self, item: Any) -> str | None:
        for attr in ("text", "content", "caption", "name"):
            value = getattr(item, attr, None)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None

    def _extract_markdown(self, item: Any) -> str | None:
        exporter = getattr(item, "export_to_markdown", None)
        if callable(exporter):
            try:
                value = exporter()
                if value:
                    return str(value)
            except Exception:  # noqa: BLE001
                pass
        return self._extract_text(item)

    def _extract_page(self, item: Any) -> int | None:
        prov = getattr(item, "prov", None)
        if prov:
            first = prov[0] if isinstance(prov, (list, tuple)) else prov
            for attr in ("page_no", "page", "page_index"):
                value = getattr(first, attr, None)
                if isinstance(value, int):
                    return value
        for attr in ("page_no", "page", "page_index"):
            value = getattr(item, attr, None)
            if isinstance(value, int):
                return value
        return None

    def _extract_page_range(self, item: Any) -> tuple[int | None, int | None]:
        pages = self._extract_pages(item)
        if not pages:
            return None, None
        return min(pages), max(pages)

    def _extract_pages(self, item: Any) -> list[int]:
        pages: list[int] = []
        prov = getattr(item, "prov", None)
        sources = list(prov) if isinstance(prov, (list, tuple)) else ([prov] if prov else [])
        sources.append(item)
        for source in sources:
            if source is None:
                continue
            for attr in ("page_no", "page", "page_index"):
                value = getattr(source, attr, None)
                if isinstance(value, int):
                    pages.append(value)
        return pages

    def _extract_bbox(self, item: Any) -> Any | None:
        prov = getattr(item, "prov", None)
        source = prov[0] if prov and isinstance(prov, (list, tuple)) else (prov or item)
        bbox = getattr(source, "bbox", None)
        return self._to_jsonable(bbox) if bbox is not None else None

    def _extract_image_ref(self, item: Any) -> str | None:
        image = getattr(item, "image", None)
        for source in (image, item):
            if source is None:
                continue
            for attr in ("uri", "path", "url"):
                value = getattr(source, attr, None)
                if value:
                    return str(value)
        return None

    def _find_text_span(self, markdown: str, text: str | None, cursor: int) -> tuple[int | None, int | None, int]:
        if not text:
            return None, None, cursor
        char_start = markdown.find(text, cursor)
        if char_start < 0:
            char_start = markdown.find(text)
        if char_start < 0:
            return None, None, cursor
        char_end = char_start + len(text)
        return char_start, char_end, max(cursor, char_end)

    def _line_range_for_span(
        self,
        markdown: str,
        char_start: int | None,
        char_end: int | None,
    ) -> tuple[int | None, int | None]:
        if char_start is None or char_end is None:
            return None, None
        line_start = markdown[:char_start].count("\n") + 1
        line_end = markdown[:char_end].count("\n") + 1
        return line_start, line_end

    def _to_jsonable(self, value: Any) -> Any | None:
        if value is None:
            return None
        if isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, (list, tuple)):
            return [self._to_jsonable(item) for item in value]
        if isinstance(value, dict):
            return {str(key): self._to_jsonable(item) for key, item in value.items()}
        if hasattr(value, "model_dump"):
            return self._to_jsonable(value.model_dump())
        if hasattr(value, "__dict__"):
            return {key: self._to_jsonable(item) for key, item in vars(value).items() if not key.startswith("_")}
        return str(value)

    def _ast_hash(self, nodes: list[CompiledNode]) -> str:
        payload = [
            {
                "node_type": node.node_type,
                "node_order": node.node_order,
                "text": node.text,
                "table_json": node.table_json,
                "image_ref": node.image_ref,
                "page_start": node.page_start,
                "page_end": node.page_end,
                "bbox": node.bbox,
                "line_start": node.line_start,
                "line_end": node.line_end,
                "char_start": node.char_start,
                "char_end": node.char_end,
            }
            for node in nodes
        ]
        return hashstr(json.dumps(payload, ensure_ascii=False, sort_keys=True))

    def _build_stats(
        self,
        *,
        markdown_content: str,
        nodes: list[CompiledNode],
        anchors: list[CompiledEvidenceAnchor],
        parser: str,
        parser_trace: list[dict[str, Any]],
        started: float,
    ) -> dict[str, Any]:
        node_type_counts = Counter(node.node_type for node in nodes)
        pages = sorted(
            {
                page
                for node in nodes
                for page in (node.page_start, node.page_end)
                if isinstance(page, int)
            }
        )
        parser_status_counts = Counter(str(item.get("status") or "unknown") for item in parser_trace)
        structured_node_count = sum(
            1 for node in nodes if str((node.metadata or {}).get("source", "")).startswith("docling.")
        )
        return {
            "node_count": len(nodes),
            "evidence_anchor_count": len(anchors),
            "character_count": len(markdown_content),
            "table_count": sum(1 for node in nodes if node.table_json is not None),
            "image_count": sum(1 for node in nodes if node.image_ref),
            "node_type_counts": dict(node_type_counts),
            "page_count": len(pages),
            "page_start": pages[0] if pages else None,
            "page_end": pages[-1] if pages else None,
            "parser": parser,
            "parser_trace_count": len(parser_trace),
            "parser_success_count": parser_status_counts.get("success", 0),
            "parser_failure_count": parser_status_counts.get("failed", 0),
            "fallback_used": self._fallback_used(parser_trace),
            "structured_node_count": structured_node_count,
            "has_docling_structure": structured_node_count > 0,
            "duration_ms": int((time.time() - started) * 1000),
        }

    def _fallback_used(self, parser_trace: list[dict[str, Any]]) -> bool:
        if len(parser_trace) <= 1:
            return False
        last_success_index = next(
            (idx for idx in range(len(parser_trace) - 1, -1, -1) if parser_trace[idx].get("status") == "success"),
            None,
        )
        if last_success_index is None:
            return any(item.get("status") == "failed" for item in parser_trace)
        return any(item.get("status") == "failed" for item in parser_trace[:last_success_index])

    def _content_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _resolve_ocr_fallbacks(self, params: dict[str, Any]) -> list[str]:
        explicit = params.get("ocr_fallbacks") or params.get("fallbacks")
        if isinstance(explicit, str):
            fallbacks = [explicit]
        elif isinstance(explicit, (list, tuple)):
            fallbacks = [str(item) for item in explicit if item]
        else:
            fallbacks = list(self.OCR_FALLBACKS)

        preferred = params.get("enable_ocr")
        if preferred and preferred != "disable" and preferred not in fallbacks:
            fallbacks.insert(0, preferred)
        return [item for item in fallbacks if item in self.OCR_PROCESSOR_TYPES]

    def _asset_type_for_suffix(self, suffix: str) -> str:
        if suffix in {".html", ".htm"}:
            return "html"
        if suffix in self.IMAGE_EXTENSIONS:
            return "image"
        if suffix:
            return "file"
        return "unknown"

    def _docling_version(self) -> str | None:
        try:
            from importlib.metadata import version

            return version("docling")
        except Exception:  # noqa: BLE001
            return None

    async def _to_thread(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        import asyncio

        return await asyncio.to_thread(func, *args, **kwargs)

    async def _read_plain_text(self, path: Path) -> str:
        async with aiofiles.open(path, encoding="utf-8") as handle:
            return await handle.read()

    def _materialized_source(self, file_path: str) -> _MaterializedSource:
        return _MaterializedSource(file_path)


class _MaterializedSource:
    def __init__(self, source: str):
        self.source = source
        self.temp_path: str | None = None

    async def __aenter__(self) -> str:
        if not _is_minio_url(self.source):
            return self.source

        bucket_name, object_name = _parse_minio_url(self.source)
        suffix = Path(object_name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            self.temp_path = temp_file.name

        from src.storage.minio.client import get_minio_client

        minio_client = get_minio_client()
        file_content = await minio_client.adownload_file(bucket_name, object_name)
        async with aiofiles.open(self.temp_path, "wb") as handle:
            await handle.write(file_content)
        logger.debug(f"Materialized MinIO source to temp file: {self.temp_path}")
        return self.temp_path

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        if self.temp_path and os.path.exists(self.temp_path):
            try:
                os.unlink(self.temp_path)
                logger.debug(f"Cleaned compiler temp file: {self.temp_path}")
            except Exception as cleanup_exc:  # noqa: BLE001
                logger.warning(f"Failed to clean compiler temp file {self.temp_path}: {cleanup_exc}")
