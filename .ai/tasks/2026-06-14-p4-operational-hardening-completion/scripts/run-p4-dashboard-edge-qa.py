from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[4]
SCREENSHOT_DIR = TASK_DIR / "screenshots"
REPORT_PATH = TASK_DIR / "p4-dashboard-qa-report.json"
SERVER_SCRIPT = TASK_DIR / "scripts" / "serve-p4-dashboard-static.ps1"
DIST_DIR = PROJECT_ROOT / "web" / "dist"
EDGE_PROFILE_DIR = TASK_DIR / "edge-cli-profile"
EDGE_CANDIDATES = [
    Path("/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
    Path("/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"),
]


def win_path(path: Path) -> str:
    return subprocess.check_output(["wslpath", "-w", str(path)], text=True).strip()


def wait_windows_http(url: str, timeout: float = 20.0) -> None:
    deadline = time.time() + timeout
    command = (
        "$ProgressPreference='SilentlyContinue'; "
        f"try {{ (Invoke-WebRequest -UseBasicParsing -Uri '{url}' -TimeoutSec 2).StatusCode; exit 0 }} "
        "catch { Write-Output $_.Exception.Message; exit 1 }"
    )
    last_output = ""
    while time.time() < deadline:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", command],
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
        last_output = (result.stdout or result.stderr or "").strip()
        if result.returncode == 0:
            return
        time.sleep(0.4)
    raise RuntimeError(f"Timed out waiting from Windows for {url}: {last_output}")


def start_static_server(port: int) -> subprocess.Popen[str]:
    process = subprocess.Popen(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            win_path(SERVER_SCRIPT),
            "-DistPath",
            win_path(DIST_DIR),
            "-Port",
            str(port),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    wait_windows_http(f"http://127.0.0.1:{port}/api/dashboard/worldline/operational-health", timeout=30)
    return process


def find_browser() -> Path:
    for candidate in EDGE_CANDIDATES:
        if candidate.exists():
            return candidate
    raise RuntimeError("Edge or Chrome executable not found")


def run_edge(args: list[str], *, timeout: int = 90) -> subprocess.CompletedProcess[str]:
    browser = find_browser()
    return subprocess.run(
        [str(browser), f"--user-data-dir={win_path(EDGE_PROFILE_DIR)}", *args],
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def extract_metrics(dom: str) -> dict[str, Any]:
    match = re.search(r'<pre id="qa-result"[^>]*>(.*?)</pre>', dom, flags=re.DOTALL)
    if not match:
        snippet = dom[-2000:] if dom else ""
        raise RuntimeError(f"QA metrics not found in dumped DOM. Tail: {snippet}")
    return json.loads(html.unescape(match.group(1)))


def dump_metrics(*, url: str, width: int, height: int) -> dict[str, Any]:
    result = run_edge(
        [
            "--headless",
            "--disable-gpu",
            f"--window-size={width},{height}",
            "--virtual-time-budget=12000",
            "--dump-dom",
            url,
        ],
        timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Edge dump-dom failed: {result.stderr or result.stdout}")
    return extract_metrics(result.stdout)


def capture_screenshot(*, url: str, width: int, height: int, path: Path) -> str:
    result = run_edge(
        [
            "--headless",
            "--disable-gpu",
            f"--window-size={width},{height}",
            "--virtual-time-budget=12000",
            f"--screenshot={win_path(path)}",
            url,
        ],
        timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Edge screenshot failed: {result.stderr or result.stdout}")
    if not path.is_file():
        raise RuntimeError(f"Screenshot was not created: {path}")
    return str(path)


def run_case(
    *,
    label: str,
    server_port: int,
    width: int,
    height: int,
    drawer: bool = False,
) -> dict[str, Any]:
    query = "?drawer=update_budgets" if drawer else ""
    url = f"http://127.0.0.1:{server_port}/qa-seed{query}"
    metrics = dump_metrics(url=url, width=width, height=height)
    screenshot = capture_screenshot(
        url=url,
        width=width,
        height=height,
        path=SCREENSHOT_DIR / f"p4-dashboard-{label}.png",
    )
    return {
        "label": label,
        "viewport": f"{width}x{height}",
        "url": url,
        "metrics": metrics,
        "screenshot": screenshot,
        "expects_drawer": drawer,
    }


def validate(report: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for item in report["checks"]:
        metrics = item["metrics"]
        label = item["label"]
        if not metrics.get("panelPresent"):
            failures.append(f"{label}: missing P4 panel")
        if item.get("expects_drawer") and not metrics.get("drawerPresent"):
            failures.append(f"{label}: missing action drawer")
        if int(metrics.get("overflowX") or 0) > 2:
            failures.append(f"{label}: horizontal overflow {metrics.get('overflowX')}")
        if metrics.get("clipped"):
            failures.append(f"{label}: clipped controls {metrics.get('clipped')}")
        if not metrics.get("metrics") or len(metrics["metrics"]) < 4:
            failures.append(f"{label}: incomplete metric cells")
    return failures


def main() -> None:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    server_port = 5194
    server: subprocess.Popen[str] | None = None
    report: dict[str, Any] = {
        "status": "failed",
        "server": f"http://127.0.0.1:{server_port}",
        "screenshots": str(SCREENSHOT_DIR),
        "checks": [],
    }
    try:
        shutil.rmtree(EDGE_PROFILE_DIR, ignore_errors=True)
        server = start_static_server(server_port)
        report["checks"].append(
            run_case(label="desktop", server_port=server_port, width=1440, height=900)
        )
        report["checks"].append(
            run_case(label="drawer", server_port=server_port, width=1440, height=900, drawer=True)
        )
        report["checks"].append(
            run_case(label="mobile", server_port=server_port, width=390, height=844)
        )
        failures = validate(report)
        report["failures"] = failures
        report["status"] = "passed" if not failures else "failed"
    finally:
        if server is not None:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
