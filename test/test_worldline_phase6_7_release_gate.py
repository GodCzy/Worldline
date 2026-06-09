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
    assert {"source", "license", "rollback"} <= set(report["review_checklist"])
    assert report["disabled_tool_policy"]["task_required_enablement_requires_review"] is True
    assert report["disabled_tool_policy"]["disabled_tools_by_server"]["worldline"] == []
    assert "OpenAI Platform" in report["connector_policy"]
    assert "GitHub" in report["connector_policy"]
    assert "Browser/Playwright" in report["connector_policy"]
    assert "remove_secrets" in report["rollback_checklist"]
    assert "revoke_remote_authorization" in report["rollback_checklist"]
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


def test_phase6_mcp_governance_detects_secret_env_keys() -> None:
    defaults = get_default_mcp_server_configs()
    defaults["worldline"]["env"]["OPENAI_API_KEY"] = "sk-test"

    report = get_mcp_governance_report(defaults)

    assert report["status"] == "failed"
    violations = {item["check"]: item for item in report["violations"]}
    assert "secrets_in_default_env" in violations
    assert violations["secrets_in_default_env"]["server"] == "worldline"


def test_phase6_mcp_governance_reports_disabled_tools_without_failure() -> None:
    defaults = get_default_mcp_server_configs()
    defaults["worldline"]["disabled_tools"] = ["worldline.run_quality_gate"]

    report = get_mcp_governance_report(defaults)

    assert report["status"] == "passed"
    assert report["disabled_tool_policy"]["disabled_tools_by_server"]["worldline"] == [
        "worldline.run_quality_gate"
    ]


def test_phase7_static_release_gate_passes_with_complete_fixture(tmp_path: Path) -> None:
    for doc_path in WorldlineReleaseGateService.REQUIRED_DOCS:
        _touch(tmp_path / doc_path)

    for task_dir in WorldlineReleaseGateService.REQUIRED_TASK_DIRS:
        _touch(tmp_path / task_dir / "EVIDENCE.md")

    _touch(
        tmp_path / "src/services/mcp_service.py",
        "\n".join(
            [
                'WORLDLINE_DEFAULT_ENABLED_MCP_SERVERS = {"worldline"}',
                '_DEFAULT_MCP_SERVERS["worldline"]["enabled"] = 1',
                '_DEFAULT_MCP_SERVERS["sequentialthinking"]["enabled"] = 0',
                '_DEFAULT_MCP_SERVERS["mcp-server-chart"]["enabled"] = 0',
                "WORLDLINE_MCP_REVIEW_CHECKLIST = ()",
                'WORLDLINE_CONNECTOR_POLICY = {"OpenAI Platform": {}}',
                "WORLDLINE_CONNECTOR_ROLLBACK_CHECKLIST = ('remove_secrets', 'revoke_remote_authorization')",
                "def get_mcp_governance_report():",
                "    return {",
                '        "disabled_tool_policy": {',
                '            "disabled_tools_by_server": {},',
                '            "task_required_enablement_requires_review": True,',
                '            "high_risk_tool_markers": [],',
                "        },",
                '        "connector_policy": {},',
                '        "rollback_checklist": ["remove_secrets", "revoke_remote_authorization"],',
                "    }",
                "    pass",
            ]
        ),
    )
    _touch(
        tmp_path / "src/services/worldline_agent_workflow_service.py",
        "\n".join(
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
    _touch(
        tmp_path / "src/services/worldline_operational_health_service.py",
        "\n".join(
            [
                "class WorldlineOperationalHealthService:",
                "    def build_report(self):",
                "        return {",
                '            "queues": {},',
                '            "failure_evidence": {},',
                '            "retry_policy": {"release_gate": "worldline_operational_readiness_contract"},',
                '            "budgets": {},',
                '            "cleanup_readiness": {},',
                "        }",
            ]
        ),
    )
    _touch(
        tmp_path / "server/routers/dashboard_router.py",
        "\n".join(
            [
                '@dashboard.get("/worldline/operational-health")',
                "async def get_worldline_operational_health():",
                "    return await WorldlineOperationalHealthService().build_report()",
            ]
        ),
    )

    skills_root = tmp_path / "codex-skills"
    for skill_name in WorldlineReleaseGateService.REQUIRED_SKILLS:
        _touch(skills_root / skill_name / "SKILL.md", f"---\nname: {skill_name}\ndescription: test\n---\n")

    screenshots_dir = tmp_path / ".ai/tasks/2026-06-03-home-theme-auth-fix/screenshots"
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
    (screenshots_dir / "ui-screenshot-report.json").write_text(
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
        "mcp_disabled_tool_policy",
        "connector_rollback_policy",
        "worldline_manifest_contract",
        "worldline_operational_readiness_contract",
        "worldline_ui_screenshot_report",
    } <= check_names
