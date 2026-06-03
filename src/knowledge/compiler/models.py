from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CompiledNode:
    """Document AST node produced by the compiler before database ids are assigned."""

    key: str
    node_type: str
    node_order: int
    parent_key: str | None = None
    text: str | None = None
    table_json: Any | None = None
    image_ref: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    bbox: Any | None = None
    line_start: int | None = None
    line_end: int | None = None
    char_start: int | None = None
    char_end: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class CompiledEvidenceAnchor:
    """Evidence anchor tied to a compiler node key."""

    node_key: str
    anchor_type: str
    source_uri: str
    page: int | None = None
    line_start: int | None = None
    line_end: int | None = None
    bbox: Any | None = None
    char_start: int | None = None
    char_end: int | None = None
    text_span: Any | None = None
    text_excerpt: str | None = None
    confidence: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class CompiledDocument:
    """Compiler output used both by legacy Markdown flow and Phase 2 persistence."""

    source_uri: str
    title: str | None
    asset_type: str
    markdown_content: str
    parser: str
    parser_version: str | None
    status: str
    content_hash: str | None = None
    ast_hash: str | None = None
    parse_config: dict[str, Any] = field(default_factory=dict)
    parser_trace: list[dict[str, Any]] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None
    nodes: list[CompiledNode] = field(default_factory=list)
    evidence_anchors: list[CompiledEvidenceAnchor] = field(default_factory=list)
