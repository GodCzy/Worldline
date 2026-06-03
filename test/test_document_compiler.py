from __future__ import annotations

from pathlib import Path

import pytest

from src.knowledge.compiler.service import DocumentCompiler


@pytest.mark.asyncio
async def test_compiler_builds_markdown_ast_and_evidence(tmp_path: Path) -> None:
    source = tmp_path / "sample.md"
    source.write_text(
        "# Title\n\n"
        "A paragraph with evidence.\n\n"
        "| Name | Value |\n"
        "| --- | --- |\n"
        "| Alpha | 1 |\n\n"
        "![diagram](images/diagram.png)\n",
        encoding="utf-8",
    )

    compiled = await DocumentCompiler().compile_file(str(source), params={"db_id": "kb_test"})

    assert compiled.status == "success"
    assert compiled.parser == "legacy_markdown"
    assert compiled.content_hash
    assert compiled.ast_hash
    assert {node.node_type for node in compiled.nodes} == {"heading", "paragraph", "table", "image"}
    assert compiled.stats["table_count"] == 1
    assert compiled.stats["image_count"] == 1
    assert compiled.stats["node_type_counts"] == {"heading": 1, "paragraph": 1, "table": 1, "image": 1}
    assert compiled.stats["parser_trace_count"] == 1
    assert compiled.stats["fallback_used"] is False
    assert compiled.nodes[0].line_start == 1
    assert compiled.nodes[1].line_start == 3
    assert len(compiled.evidence_anchors) == len(compiled.nodes)
    assert all(anchor.source_uri == str(source) for anchor in compiled.evidence_anchors)
    assert compiled.evidence_anchors[0].line_start == 1
    assert compiled.evidence_anchors[0].text_span == {"start": 0, "end": 7}


@pytest.mark.asyncio
async def test_compiler_uses_docling_primary_for_supported_documents(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "deck.pptx"
    source.write_bytes(b"fake")

    class FakeStatus:
        name = "SUCCESS"

    class FakeProv:
        page_no = 2
        bbox = {"l": 1, "t": 2, "r": 3, "b": 4}

    class FakeText:
        text = "Docling paragraph"
        label = "paragraph"
        prov = [FakeProv()]

    class FakeTable:
        data = {"rows": [["A", "B"], ["1", "2"]]}
        prov = [FakeProv()]

        def export_to_markdown(self) -> str:
            return "| A | B |\n| --- | --- |\n| 1 | 2 |"

    class FakeImage:
        text = "A chart"
        image = type("Image", (), {"uri": "minio://kb-images/chart.png"})()
        prov = [FakeProv()]

    class FakeDoc:
        texts = [FakeText()]
        tables = [FakeTable()]
        pictures = [FakeImage()]

        def iterate_items(self):
            return iter([(self.texts[0], 0), (self.tables[0], 0), (self.pictures[0], 0)])

    class FakeResult:
        status = FakeStatus()
        document = FakeDoc()

    class FakeConverter:
        def convert(self, _path: Path) -> FakeResult:
            return FakeResult()

    monkeypatch.setattr("src.knowledge.compiler.service._get_docling_converter", lambda: FakeConverter())
    monkeypatch.setattr(
        "src.knowledge.compiler.service._convert_with_docling",
        lambda _path, _params: "Docling paragraph\n\n| A | B |\n| --- | --- |\n| 1 | 2 |\n\n![chart](minio://kb-images/chart.png)",
    )

    compiled = await DocumentCompiler().compile_file(str(source), params={"db_id": "kb_test"})

    assert compiled.status == "success"
    assert compiled.parser == "docling"
    assert compiled.parser_trace[0] == {"parser": "docling", "status": "success"}
    assert {node.node_type for node in compiled.nodes} == {"paragraph", "table", "image"}
    assert compiled.nodes[0].bbox == {"l": 1, "t": 2, "r": 3, "b": 4}
    assert compiled.nodes[1].char_start is not None
    assert compiled.nodes[2].char_start is not None
    assert compiled.nodes[0].metadata["source"] == "docling.text"
    assert compiled.nodes[1].metadata["source"] == "docling.table"
    assert compiled.stats["has_docling_structure"] is True
    assert compiled.stats["structured_node_count"] == 3
    assert compiled.stats["page_count"] == 1
    assert compiled.evidence_anchors[0].page == 2
    assert compiled.evidence_anchors[1].line_start is not None


@pytest.mark.asyncio
async def test_compiler_records_ocr_fallback_after_docling_failure(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "scanned.pdf"
    source.write_bytes(b"fake")

    class FailingConverter:
        def convert(self, _path: Path):
            raise RuntimeError("docling failed")

    def fake_process_file(processor_type: str, _file_path: str, _params: dict | None = None) -> str:
        assert processor_type == "onnx_rapid_ocr"
        return "OCR fallback text"

    monkeypatch.setattr("src.knowledge.compiler.service._get_docling_converter", lambda: FailingConverter())
    monkeypatch.setattr("src.knowledge.compiler.service._process_ocr_file", fake_process_file)

    compiled = await DocumentCompiler().compile_file(
        str(source),
        params={"db_id": "kb_test", "ocr_fallbacks": ["onnx_rapid_ocr"]},
    )

    assert compiled.status == "success"
    assert compiled.parser == "onnx_rapid_ocr"
    assert compiled.markdown_content == "OCR fallback text"
    assert compiled.parser_trace[0]["parser"] == "docling"
    assert compiled.parser_trace[0]["status"] == "failed"
    assert compiled.parser_trace[1] == {"parser": "onnx_rapid_ocr", "status": "success"}
    assert compiled.stats["fallback_used"] is True
    assert compiled.stats["parser_failure_count"] == 1
    assert compiled.stats["parser_success_count"] == 1


@pytest.mark.asyncio
async def test_compiler_returns_failed_document_with_parser_trace(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "broken.png"
    source.write_bytes(b"fake")

    def failing_process_file(processor_type: str, _file_path: str, _params: dict | None = None) -> str:
        raise RuntimeError(f"{processor_type} unavailable")

    async def failing_legacy(_path: str, params: dict | None = None) -> str:
        raise RuntimeError("legacy parser failed")

    monkeypatch.setattr("src.knowledge.compiler.service._process_ocr_file", failing_process_file)
    monkeypatch.setattr("src.knowledge.compiler.service._process_file_to_markdown", failing_legacy)

    compiled = await DocumentCompiler().compile_file(
        str(source),
        params={"db_id": "kb_test", "ocr_fallbacks": ["onnx_rapid_ocr"]},
    )

    assert compiled.status == "failed"
    assert compiled.error_message == "legacy parser failed"
    assert compiled.nodes == []
    assert compiled.evidence_anchors == []
    assert [item["status"] for item in compiled.parser_trace] == ["failed", "failed", "failed"]
    assert compiled.stats["parser_failure_count"] == 3
    assert compiled.stats["fallback_used"] is True
