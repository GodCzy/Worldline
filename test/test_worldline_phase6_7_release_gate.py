from __future__ import annotations

import json
from pathlib import Path

from src.services.mcp_service import get_default_mcp_server_configs, get_mcp_governance_report
from src.services.worldline_release_gate_service import WorldlineReleaseGateService


def _touch(path: Path, content: str = "# Test\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_phase6_mcp_defaults_are_controlled() -> None:
    defaults = get_default_mcp_server_configs()
    report = get_mcp_governance_report(defaults)

    assert report["status"] == "passed"
    assert report["servers"]["enabled_by_default"] == ["worldline"]
    assert "sequentialthinking" in report["servers"]["disabled_by_default"]
    assert "mcp-server-chart" in report["servers"]["disabled_by_default"]
    assert report["violations"] == []
    assert defaults["worldline"]["enabled"] == 1
    assert defaults["sequentialthinking"]["enabled"] == 0
    assert defaults["mcp-server-chart"]["enabled"] == 0


def test_phase6_mcp_governance_detects_unexpected_enabled_server() -> None:
    defaults = get_default_mcp_server_configs()
    defaults["mcp-server-chart"]["enabled"] = 1

    report = get_mcp_governance_report(defaults)

    assert report["status"] == "failed"
    checks = {item["check"] for item in report["violations"]}
    assert "default_enabled_allowlist" in checks
    assert "conditional_default_disabled" in checks


def test_phase7_static_release_gate_passes_with_complete_fixture(tmp_path: Path) -> None:
    for doc_path in WorldlineReleaseGateService.REQUIRED_DOCS:
        _touch(tmp_path / doc_path)

    for task_dir in WorldlineReleaseGateService.REQUIRED_TASK_DIRS:
        _touch(tmp_path / task_dir / "EVIDENCE.md")

    _touch(
        tmp_path / "src/services/mcp_service.py",
        '\n'.join(
            [
                'WORLDLINE_DEFAULT_ENABLED_MCP_SERVERS = {"worldline"}',
                '_DEFAULT_MCP_SERVERS["worldline"]["enabled"] = 1',
                '_DEFAULT_MCP_SERVERS["sequentialthinking"]["enabled"] = 0',
                '_DEFAULT_MCP_SERVERS["mcp-server-chart"]["enabled"] = 0',
                "def get_mcp_governance_report():",
                "    pass",
            ]
        ),
    )
    _touch(
        tmp_path / "src/services/worldline_agent_workflow_service.py",
        '\n'.join(
            [
                'SERVER_NAME = "worldline"',
                '"external_agents_direct_db_write": False',
                '"all_write_tools_require_admin": True',
                '"table": "worldline_mcp_audit_logs"',
                '"single_writer_policy": True',
                '"parallel_writes_to_same_files": False',
                '"name": "worldline.compile_document"',
                '"name": "worldline.rebuild_wiki"',
                '"name": "worldline.update_graph"',
                '"name": "worldline.run_quality_gate"',
                '"name": "worldline.inspect_timeline"',
                '"lane": "research_reviewer"',
                '"lane": "knowledge_operator"',
                '"lane": "frontend_qa"',
                '"lane": "release_auditor"',
            ]
        ),
    )

    skills_root = tmp_path / "codex-skills"
    for skill_name in WorldlineReleaseGateService.REQUIRED_SKILLS:
        _touch(skills_root / skill_name / "SKILL.md", f"---\nname: {skill_name}\ndescription: test\n---\n")

    screenshots_dir = tmp_path / ".ai/tasks/2026-06-03-phase5-worldline-ui/screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    report_items = []
    for page in WorldlineReleaseGateService.REQUIRED_SCREENSHOT_PAGES:
        for viewport in WorldlineReleaseGateService.REQUIRED_SCREENSHOT_VIEWPORTS:
            screenshot = screenshots_dir / f"{page}-{viewport}.png"
            screenshot.write_bytes(b"\x89PNG\r\n\x1a\n")
            report_items.append(
                {
                    "page": page,
                    "viewport": viewport,
                    "screenshot": str(screenshot),
                }
            )
    (screenshots_dir / "phase5-screenshot-report.json").write_text(
        json.dumps({"report": report_items, "failures": []}),
        encoding="utf-8",
    )

    service = WorldlineReleaseGateService(project_root=tmp_path, codex_skills_root=skills_root)
    report = service.run_static_gate()

    assert report["status"] == "passed"
    assert report["summary"]["failed_count"] == 0
    check_names = {check["name"] for check in report["checks"]}
    assert {
        "required_docs_present",
        "phase_task_dirs_present",
        "codex_worldline_skills_installed",
        "mcp_default_governance",
        "worldline_manifest_contract",
        "phase5_screenshot_report",
    } <= check_names
