from __future__ import annotations

import json
import os
import datetime as dt
import re
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
        "docs/architecture/operational-hardening.md",
        "docs/architecture/evaluation-gates.md",
        "docs/product/worldline-completion-matrix.md",
    )
    REQUIRED_TASK_DIRS = (
        ".ai/tasks/2026-06-03-worldline-reset",
        ".ai/tasks/2026-06-03-worldline-frontier-stack",
        ".ai/tasks/2026-06-03-knowledge-compiler-v1",
        ".ai/tasks/2026-06-03-phase3-4-wiki-graph",
        ".ai/tasks/2026-06-03-home-theme-auth-fix",
        ".ai/tasks/2026-06-03-phase6-7-governance-release",
        ".ai/tasks/2026-06-15-p5-public-demo-share-export",
    )
    REQUIRED_SKILLS = (
        "worldline-orient",
        "worldline-knowledge-pipeline",
        "worldline-backend-contract",
        "worldline-frontend-workbench",
        "worldline-mcp-governance",
        "worldline-eval-release",
    )
    REQUIRED_SCREENSHOT_PAGES = {"home", "themes", "worldline-hub", "agent-login-redirect", "authenticated-sidebar"}
    REQUIRED_SCREENSHOT_VIEWPORTS = {"1920x1080", "1440x900", "390x844"}
    PUBLIC_DEMO_QA_REPORT = ".ai/tasks/2026-06-15-p5-public-demo-share-export/p5-public-demo-qa-report.json"
    PUBLIC_DEMO_SECRET_SCAN_PATHS = (
        "docs/product/public-demo.md",
        "docs/product/worldline-completion-matrix.md",
        "src/services/worldline_public_demo_service.py",
        "server/routers/worldline_public_demo_router.py",
        "server/utils/auth_middleware.py",
        "web/src/apis/worldline_api.js",
        "web/src/router/index.js",
        "web/src/views/worldline/WorldlinePublicShareView.vue",
        ".ai/tasks/2026-06-15-p5-public-demo-share-export/ALIGNMENT.md",
        ".ai/tasks/2026-06-15-p5-public-demo-share-export/DESIGN.md",
        ".ai/tasks/2026-06-15-p5-public-demo-share-export/EVIDENCE.md",
    )
    PUBLIC_DEMO_SECRET_PATTERNS = (
        re.compile(r"sk-[A-Za-z0-9_\-]{20,}"),
        re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
        re.compile(r"AKIA[0-9A-Z]{16}"),
        re.compile(r"(?i)\b(password|passwd|secret)\s*[:=]\s*[^\s,;]{6,}"),
        re.compile(r"(?i)\btoken\s*[:=]\s*[A-Za-z0-9_\-\.]{12,}"),
        re.compile(r"(?i)\b(api[_-]?key)\s*[:=]\s*[A-Za-z0-9_\-\.]{12,}"),
    )

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
        checks.append(self._operational_readiness_check())
        checks.append(self._public_demo_readiness_check())
        checks.append(self._public_demo_secret_hygiene_check())
        checks.append(self._public_demo_screenshot_check())
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
        default_fragments = [
            'WORLDLINE_DEFAULT_ENABLED_MCP_SERVERS = {"worldline"}',
            '_DEFAULT_MCP_SERVERS["worldline"]["enabled"] = 1',
            '_DEFAULT_MCP_SERVERS["sequentialthinking"]["enabled"] = 0',
            '_DEFAULT_MCP_SERVERS["mcp-server-chart"]["enabled"] = 0',
            "def get_mcp_governance_report(",
        ]
        disabled_tool_fragments = [
            "WORLDLINE_MCP_REVIEW_CHECKLIST",
            '"disabled_tool_policy"',
            '"disabled_tools_by_server"',
            '"task_required_enablement_requires_review"',
            '"high_risk_tool_markers"',
        ]
        connector_rollback_fragments = [
            "WORLDLINE_CONNECTOR_POLICY",
            "WORLDLINE_CONNECTOR_ROLLBACK_CHECKLIST",
            '"connector_policy"',
            '"rollback_checklist"',
            '"OpenAI Platform"',
            '"remove_secrets"',
            '"revoke_remote_authorization"',
        ]
        default_missing = [fragment for fragment in default_fragments if fragment not in source]
        disabled_tool_missing = [fragment for fragment in disabled_tool_fragments if fragment not in source]
        connector_rollback_missing = [
            fragment for fragment in connector_rollback_fragments if fragment not in source
        ]
        return [
            {
                "name": "mcp_default_governance",
                "passed": not default_missing,
                "severity": "required",
                "details": {
                    "policy": {
                        "default_enabled_allowlist": ["worldline"],
                        "conditional_servers": ["mcp-server-chart", "sequentialthinking"],
                        "external_agent_write_boundary": "worldline_service_boundary",
                        "external_codex_tools": ["GitHub", "Browser/Playwright"],
                    },
                    "missing_source_fragments": default_missing,
                },
            },
            {
                "name": "mcp_disabled_tool_policy",
                "passed": not disabled_tool_missing,
                "severity": "required",
                "details": {
                    "policy": {
                        "task_required_enablement_requires_review": True,
                        "conditional_servers_disabled_by_default": [
                            "mcp-server-chart",
                            "sequentialthinking",
                        ],
                    },
                    "missing_source_fragments": disabled_tool_missing,
                },
            },
            {
                "name": "connector_rollback_policy",
                "passed": not connector_rollback_missing,
                "severity": "required",
                "details": {
                    "required": [
                        "connector_policy",
                        "rollback_checklist",
                        "remove_secrets",
                        "revoke_remote_authorization",
                    ],
                    "missing_source_fragments": connector_rollback_missing,
                },
            },
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

    def _operational_readiness_check(self) -> dict[str, Any]:
        service_source = self._read_project_file("src/services/worldline_operational_health_service.py")
        action_source = self._read_project_file("src/services/worldline_operational_action_service.py")
        router_source = self._read_project_file("server/routers/dashboard_router.py")
        service_fragments = [
            "class WorldlineOperationalHealthService",
            '"queues"',
            '"failure_evidence"',
            '"retry_policy"',
            '"budgets"',
            '"cleanup_readiness"',
            '"operation_controls"',
            "worldline_operational_readiness_contract",
        ]
        action_fragments = [
            "class WorldlineOperationalActionService",
            "async def requeue_failed",
            "async def mark_source_stale",
            "async def update_budgets",
            "async def cleanup",
            "worldline.operational_requeue",
            "worldline.operational_cleanup",
        ]
        router_fragments = [
            '@dashboard.get("/worldline/operational-health")',
            "WorldlineOperationalHealthService().build_report",
            '@dashboard.post("/worldline/operational-health/actions")',
            "WorldlineOperationalActionService().run_action",
        ]
        missing_service = [fragment for fragment in service_fragments if fragment not in service_source]
        missing_action = [fragment for fragment in action_fragments if fragment not in action_source]
        missing_router = [fragment for fragment in router_fragments if fragment not in router_source]
        return {
            "name": "worldline_operational_readiness_contract",
            "passed": not missing_service and not missing_action and not missing_router,
            "severity": "required",
            "details": {
                "service": "WorldlineOperationalHealthService",
                "admin_endpoint": "/api/dashboard/worldline/operational-health",
                "action_service": "WorldlineOperationalActionService",
                "action_endpoint": "/api/dashboard/worldline/operational-health/actions",
                "missing_service_fragments": missing_service,
                "missing_action_fragments": missing_action,
                "missing_router_fragments": missing_router,
            },
        }

    def _public_demo_readiness_check(self) -> dict[str, Any]:
        service_source = self._read_project_file("src/services/worldline_public_demo_service.py")
        router_source = self._read_project_file("server/routers/worldline_public_demo_router.py")
        auth_source = self._read_project_file("server/utils/auth_middleware.py")
        api_source = self._read_project_file("web/src/apis/worldline_api.js")
        web_router_source = self._read_project_file("web/src/router/index.js")
        share_view_source = self._read_project_file("web/src/views/worldline/WorldlinePublicShareView.vue")
        docs_source = self._read_project_file("docs/product/public-demo.md")
        matrix_source = self._read_project_file("docs/product/worldline-completion-matrix.md")

        service_fragments = [
            "class WorldlinePublicDemoService",
            "PUBLIC_DEMO_DATASET",
            "def get_branch_share",
            "def build_evidence_bundle",
            "def build_bundle_markdown",
            "def safety_report",
            '"readOnly": True',
        ]
        router_fragments = [
            '@worldline_public_demo.get("/dataset")',
            '@worldline_public_demo.get("/branches/{share_id}")',
            '@worldline_public_demo.get("/evidence-bundle")',
            "PlainTextResponse",
        ]
        public_boundary_fragments = [
            r"^/api/worldline/public-demo(?:/.*)?$",
            "worldlinePublicDemoApi",
            "apiGet('/api/worldline/public-demo/dataset', {}, false)",
            "path: 'share/:shareId'",
            "WorldlinePublicShareView",
            'data-worldline-public-share="true"',
            'data-evidence-bundle-export="true"',
        ]
        docs_fragments = [
            "P5 Public Demo",
            "/worldline/share/demo-branch-evidence",
            "Rollback",
            "JSON evidence bundle",
            "Markdown evidence bundle",
        ]
        matrix_fragments = [
            "| Public demo dataset | Done |",
            "| Read-only shared branch views | Done |",
            "| Evidence bundle export | Done |",
            "| GitHub PR/issue integration | External |",
            "| Optional ingestion tools | External |",
        ]

        missing = {
            "service": [item for item in service_fragments if item not in service_source],
            "router": [item for item in router_fragments if item not in router_source],
            "public_boundary": [
                item
                for item in public_boundary_fragments
                if item not in f"{auth_source}\n{api_source}\n{web_router_source}\n{share_view_source}"
            ],
            "docs": [item for item in docs_fragments if item not in docs_source],
            "matrix": [item for item in matrix_fragments if item not in matrix_source],
        }
        passed = not any(missing.values())
        return {
            "name": "worldline_public_demo_readiness_contract",
            "passed": passed,
            "severity": "required",
            "details": {
                "dataset_endpoint": "/api/worldline/public-demo/dataset",
                "share_route": "/worldline/share/demo-branch-evidence",
                "bundle_endpoint": "/api/worldline/public-demo/evidence-bundle",
                "external_rows_remain_gated": ["GitHub PR/issue integration", "Optional ingestion tools"],
                "missing_fragments": missing,
            },
        }

    def _public_demo_secret_hygiene_check(self) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []
        missing_files = []
        scanned_files = []
        for relative_path in self.PUBLIC_DEMO_SECRET_SCAN_PATHS:
            path = self.project_root / relative_path
            if not path.is_file():
                missing_files.append(relative_path)
                continue
            scanned_files.append(relative_path)
            text = path.read_text(encoding="utf-8")
            for pattern in self.PUBLIC_DEMO_SECRET_PATTERNS:
                for match in pattern.finditer(text):
                    findings.append(
                        {
                            "path": relative_path,
                            "pattern": pattern.pattern,
                            "sample": self._redact_secret_like_value(match.group(0)),
                        }
                    )
        return {
            "name": "worldline_public_demo_secret_hygiene",
            "passed": not findings and not missing_files,
            "severity": "required",
            "details": {
                "scanned_files": scanned_files,
                "missing_files": missing_files,
                "finding_count": len(findings),
                "findings": findings[:20],
            },
        }

    def _public_demo_screenshot_check(self) -> dict[str, Any]:
        report_path = self.project_root / self.PUBLIC_DEMO_QA_REPORT
        if not report_path.is_file():
            return {
                "name": "worldline_public_demo_screenshot_report",
                "passed": False,
                "severity": "required",
                "details": {"missing": str(report_path)},
            }

        try:
            payload = json.loads(report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return {
                "name": "worldline_public_demo_screenshot_report",
                "passed": False,
                "severity": "required",
                "details": {"error": str(exc), "path": str(report_path)},
            }

        checks = payload.get("checks") or []
        labels = {item.get("label") for item in checks}
        missing_labels = sorted({"desktop", "mobile"} - labels)
        missing_files = [
            item.get("screenshot")
            for item in checks
            if item.get("screenshot") and not self._screenshot_path_exists(str(item["screenshot"]))
        ]
        failures = payload.get("failures") or []
        passed = payload.get("status") == "passed" and not failures and not missing_labels and not missing_files
        return {
            "name": "worldline_public_demo_screenshot_report",
            "passed": passed,
            "severity": "required",
            "details": {
                "path": str(report_path),
                "status": payload.get("status"),
                "check_count": len(checks),
                "missing_labels": missing_labels,
                "missing_files": missing_files,
                "failure_count": len(failures),
            },
        }

    def _screenshot_check(self) -> dict[str, Any]:
        report_path = (
            self.project_root
            / ".ai/tasks/2026-06-03-home-theme-auth-fix/screenshots/ui-screenshot-report.json"
        )
        if not report_path.is_file():
            return {
                "name": "worldline_ui_screenshot_report",
                "passed": False,
                "severity": "required",
                "details": {"missing": str(report_path)},
            }

        try:
            payload = json.loads(report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return {
                "name": "worldline_ui_screenshot_report",
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
            "name": "worldline_ui_screenshot_report",
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
    def _redact_secret_like_value(value: str) -> str:
        if len(value) <= 8:
            return "***"
        return f"{value[:4]}...{value[-4:]}"

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
