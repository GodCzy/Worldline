from __future__ import annotations

import json
import os
import datetime as dt
from pathlib import Path
from typing import Any


class WorldlineReleaseGateService:
    """Static project release gate for Phase 6/7 public-demo readiness."""

    REQUIRED_DOCS = (
        "README.md",
        "AGENTS.md",
        "docs/index.md",
        "docs/product/worldline-project-book.md",
        "docs/product/public-demo.md",
        "docs/architecture/knowledge-compiler.md",
        "docs/architecture/llm-wiki.md",
        "docs/architecture/temporal-evidence-graph.md",
        "docs/architecture/worldline-ui.md",
        "docs/architecture/mcp-skill-governance.md",
        "docs/architecture/evaluation-gates.md",
    )
    REQUIRED_TASK_DIRS = (
        ".ai/tasks/2026-06-03-worldline-reset",
        ".ai/tasks/2026-06-03-worldline-frontier-stack",
        ".ai/tasks/2026-06-03-knowledge-compiler-v1",
        ".ai/tasks/2026-06-03-phase3-4-wiki-graph",
        ".ai/tasks/2026-06-03-phase5-worldline-ui",
        ".ai/tasks/2026-06-03-phase6-7-governance-release",
    )
    REQUIRED_SKILLS = (
        "worldline-orient",
        "worldline-knowledge-pipeline",
        "worldline-backend-contract",
        "worldline-frontend-workbench",
        "worldline-mcp-governance",
        "worldline-eval-release",
    )
    REQUIRED_SCREENSHOT_PAGES = {"worldline-hub", "worldline-workbench", "graph"}
    REQUIRED_SCREENSHOT_VIEWPORTS = {"1920x1080", "1440x900", "390x844"}

    def __init__(
        self,
        *,
        project_root: str | Path | None = None,
        codex_skills_root: str | Path | None = None,
    ) -> None:
        self.project_root = Path(project_root or self._default_project_root()).resolve()
        self.codex_skills_root = Path(codex_skills_root or self._default_codex_skills_root()).resolve()

    def run_static_gate(self) -> dict[str, Any]:
        checks: list[dict[str, Any]] = []
        checks.extend(self._doc_checks())
        checks.extend(self._task_checks())
        checks.extend(self._skill_checks())
        checks.extend(self._mcp_checks())
        checks.extend(self._manifest_checks())
        checks.append(self._screenshot_check())

        failed = [check for check in checks if not check["passed"]]
        return {
            "status": "passed" if not failed else "failed",
            "phase": "phase6_7_release",
            "project_root": str(self.project_root),
            "codex_skills_root": str(self.codex_skills_root),
            "generated_at": dt.datetime.now(dt.UTC).replace(tzinfo=None).isoformat(),
            "summary": {
                "check_count": len(checks),
                "passed_count": len(checks) - len(failed),
                "failed_count": len(failed),
            },
            "checks": checks,
            "next_step": "ready_for_phase6_7_demo" if not failed else "fix_failed_release_gate_checks",
        }

    def write_report(self, output_path: str | Path) -> dict[str, Any]:
        report = self.run_static_gate()
        path = Path(output_path)
        if not path.is_absolute():
            path = self.project_root / path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return report

    def _doc_checks(self) -> list[dict[str, Any]]:
        missing = [path for path in self.REQUIRED_DOCS if not (self.project_root / path).is_file()]
        return [
            {
                "name": "required_docs_present",
                "passed": not missing,
                "severity": "required",
                "details": {
                    "required": list(self.REQUIRED_DOCS),
                    "missing": missing,
                },
            }
        ]

    def _task_checks(self) -> list[dict[str, Any]]:
        missing = [path for path in self.REQUIRED_TASK_DIRS if not (self.project_root / path).is_dir()]
        evidence_missing = [
            path
            for path in self.REQUIRED_TASK_DIRS
            if (self.project_root / path).is_dir() and not (self.project_root / path / "EVIDENCE.md").is_file()
        ]
        return [
            {
                "name": "phase_task_dirs_present",
                "passed": not missing and not evidence_missing,
                "severity": "required",
                "details": {
                    "required": list(self.REQUIRED_TASK_DIRS),
                    "missing": missing,
                    "evidence_missing": evidence_missing,
                },
            }
        ]

    def _skill_checks(self) -> list[dict[str, Any]]:
        missing = [
            name
            for name in self.REQUIRED_SKILLS
            if not (self.codex_skills_root / name / "SKILL.md").is_file()
        ]
        return [
            {
                "name": "codex_worldline_skills_installed",
                "passed": not missing,
                "severity": "required",
                "details": {
                    "required": list(self.REQUIRED_SKILLS),
                    "missing": missing,
                },
            }
        ]

    def _mcp_checks(self) -> list[dict[str, Any]]:
        source = self._read_project_file("src/services/mcp_service.py")
        expected_fragments = [
            'WORLDLINE_DEFAULT_ENABLED_MCP_SERVERS = {"worldline"}',
            '_DEFAULT_MCP_SERVERS["worldline"]["enabled"] = 1',
            '_DEFAULT_MCP_SERVERS["sequentialthinking"]["enabled"] = 0',
            '_DEFAULT_MCP_SERVERS["mcp-server-chart"]["enabled"] = 0',
            "def get_mcp_governance_report(",
        ]
        missing = [fragment for fragment in expected_fragments if fragment not in source]
        report = {
            "status": "passed" if not missing else "failed",
            "policy": {
                "default_enabled_allowlist": ["worldline"],
                "conditional_servers": ["mcp-server-chart", "sequentialthinking"],
                "external_agent_write_boundary": "worldline_service_boundary",
                "external_codex_tools": ["GitHub", "Browser/Playwright"],
            },
            "missing_source_fragments": missing,
        }
        return [
            {
                "name": "mcp_default_governance",
                "passed": report["status"] == "passed",
                "severity": "required",
                "details": report,
            }
        ]

    def _manifest_checks(self) -> list[dict[str, Any]]:
        source = self._read_project_file("src/services/worldline_agent_workflow_service.py")
        expected_fragments = [
            'SERVER_NAME = "worldline"',
            '"external_agents_direct_db_write": False',
            '"all_write_tools_require_admin": True',
            '"table": "worldline_mcp_audit_logs"',
            '"single_writer_policy": True',
            '"parallel_writes_to_same_files": False',
            '"lane": "research_reviewer"',
            '"lane": "knowledge_operator"',
            '"lane": "frontend_qa"',
            '"lane": "release_auditor"',
        ]
        failed_details = [fragment for fragment in expected_fragments if fragment not in source]
        tool_count = source.count('"name": "worldline.')
        write_tool_count = sum(
            fragment in source
            for fragment in (
                '"name": "worldline.compile_document"',
                '"name": "worldline.rebuild_wiki"',
                '"name": "worldline.update_graph"',
                '"name": "worldline.run_quality_gate"',
            )
        )
        subagent_lane_count = source.count('"lane": "')

        return [
            {
                "name": "worldline_manifest_contract",
                "passed": not failed_details,
                "severity": "required",
                "details": {
                    "server": {"name": "worldline"},
                    "tool_count": tool_count,
                    "write_tool_count": write_tool_count,
                    "subagent_lane_count": subagent_lane_count,
                    "failures": failed_details,
                },
            }
        ]

    def _screenshot_check(self) -> dict[str, Any]:
        report_path = (
            self.project_root
            / ".ai/tasks/2026-06-03-phase5-worldline-ui/screenshots/phase5-screenshot-report.json"
        )
        if not report_path.is_file():
            return {
                "name": "phase5_screenshot_report",
                "passed": False,
                "severity": "required",
                "details": {"missing": str(report_path)},
            }

        try:
            payload = json.loads(report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return {
                "name": "phase5_screenshot_report",
                "passed": False,
                "severity": "required",
                "details": {"error": str(exc), "path": str(report_path)},
            }

        report_items = payload.get("report") or []
        pages = {item.get("page") for item in report_items}
        viewports = {item.get("viewport") for item in report_items}
        missing_pages = sorted(self.REQUIRED_SCREENSHOT_PAGES - pages)
        missing_viewports = sorted(self.REQUIRED_SCREENSHOT_VIEWPORTS - viewports)
        failures = payload.get("failures") or []
        missing_files = [
            item.get("screenshot")
            for item in report_items
            if item.get("screenshot") and not self._screenshot_path_exists(str(item["screenshot"]))
        ]
        passed = not failures and not missing_pages and not missing_viewports and not missing_files
        return {
            "name": "phase5_screenshot_report",
            "passed": passed,
            "severity": "required",
            "details": {
                "path": str(report_path),
                "screenshot_count": len(report_items),
                "failure_count": len(failures),
                "missing_pages": missing_pages,
                "missing_viewports": missing_viewports,
                "missing_files": missing_files,
            },
        }

    def _screenshot_path_exists(self, value: str) -> bool:
        path = Path(value)
        if path.is_file():
            return True
        if value.startswith("/mnt/d/"):
            windows_path = Path("D:/") / value.removeprefix("/mnt/d/")
            return windows_path.is_file()
        return (self.project_root / value).is_file()

    def _read_project_file(self, relative_path: str) -> str:
        path = self.project_root / relative_path
        if not path.is_file():
            return ""
        return path.read_text(encoding="utf-8")

    @staticmethod
    def _default_project_root() -> Path:
        return Path(__file__).resolve().parents[2]

    @staticmethod
    def _default_codex_skills_root() -> Path:
        env_root = os.environ.get("CODEX_SKILLS_ROOT")
        if env_root:
            return Path(env_root)

        candidates = [
            Path.home() / ".codex" / "skills",
            Path("/mnt/c/Users/Joy/.codex/skills"),
            Path("C:/Users/Joy/.codex/skills"),
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return candidates[0]
