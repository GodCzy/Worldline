param(
  [string]$DistPath = "D:\dev\Worldline\web\dist",
  [int]$Port = 5195
)

$ErrorActionPreference = "Stop"

$distRoot = [System.IO.Path]::GetFullPath($DistPath)
if (-not (Test-Path -LiteralPath $distRoot -PathType Container)) {
  throw "DistPath does not exist: $distRoot"
}

$listener = [System.Net.HttpListener]::new()
$prefix = "http://127.0.0.1:$Port/"
$listener.Prefixes.Add($prefix)

function Write-Bytes {
  param(
    [System.Net.HttpListenerContext]$Context,
    [byte[]]$Bytes,
    [string]$ContentType,
    [int]$StatusCode = 200
  )
  $Context.Response.StatusCode = $StatusCode
  $Context.Response.ContentType = $ContentType
  $Context.Response.ContentLength64 = $Bytes.Length
  $Context.Response.OutputStream.Write($Bytes, 0, $Bytes.Length)
  $Context.Response.OutputStream.Close()
}

function Write-Text {
  param(
    [System.Net.HttpListenerContext]$Context,
    [string]$Text,
    [string]$ContentType = "text/plain; charset=utf-8",
    [int]$StatusCode = 200
  )
  Write-Bytes -Context $Context -Bytes ([System.Text.Encoding]::UTF8.GetBytes($Text)) -ContentType $ContentType -StatusCode $StatusCode
}

function Write-Json {
  param(
    [System.Net.HttpListenerContext]$Context,
    [object]$Payload,
    [int]$StatusCode = 200
  )
  $json = $Payload | ConvertTo-Json -Depth 30
  Write-Text -Context $Context -Text $json -ContentType "application/json; charset=utf-8" -StatusCode $StatusCode
}

function Get-ContentType {
  param([string]$Path)
  switch ([System.IO.Path]::GetExtension($Path).ToLowerInvariant()) {
    ".html" { "text/html; charset=utf-8" }
    ".js" { "text/javascript; charset=utf-8" }
    ".css" { "text/css; charset=utf-8" }
    ".json" { "application/json; charset=utf-8" }
    ".svg" { "image/svg+xml" }
    ".png" { "image/png" }
    ".jpg" { "image/jpeg" }
    ".jpeg" { "image/jpeg" }
    ".webp" { "image/webp" }
    ".ico" { "image/x-icon" }
    default { "application/octet-stream" }
  }
}

function New-SharePayload {
  @{
    protocolVersion = "worldline-public-demo-v0.1"
    shareId = "demo-branch-evidence"
    readOnly = $true
    mode = "read_only"
    generatedAt = "2026-06-15T00:00:00Z"
    dataset = @{
      datasetId = "worldline-public-demo-safety-v1"
      title = "Worldline Public Demo Dataset"
      generatedAt = "2026-06-15T00:00:00Z"
      checksum = "sha256:static-qa"
      sourceMaterial = @(
        @{ id = "src-public-demo-doc"; label = "Public demo contract"; sourceUri = "docs/product/public-demo.md"; lineStart = 1 }
      )
      shareViews = @(
        @{ shareId = "demo-branch-evidence"; route = "/worldline/share/demo-branch-evidence"; mode = "read_only" }
      )
    }
    share = @{
      shareId = "demo-branch-evidence"
      route = "/worldline/share/demo-branch-evidence"
      branchId = "branch-evidence"
      mode = "read_only"
      allowedActions = @("inspect", "download_json_bundle", "download_markdown_bundle")
    }
    branch = @{
      id = "branch-evidence"
      title = "Evidence-first branch"
      hypothesis = "A public share is safe only when each visible claim links to curated evidence."
      evidenceIds = @("ev-public-demo-doc", "ev-release-gate", "ev-share-route")
      wikiRefs = @("wiki-public-demo")
      entityRefs = @("entity-public-demo-service", "entity-read-only-share")
      timelineRefs = @("tf-public-demo-freeze")
    }
    worldline = @{
      activeBranchId = "branch-evidence"
      selectedNodeId = "branch-evidence"
      displayMeta = @{
        stageLabel = "PUBLIC DEMO"
        stageTitle = "Read-only evidence branch"
        stageSubtitle = "A safe branch share with evidence, graph, timeline, and replay export."
      }
      tree = @{
        width = 1100
        height = 620
        nodes = @(
          @{ id = "root"; type = "root"; label = "Share safely"; title = "Public demo start"; x = 90; y = 310 },
          @{ id = "branch-evidence"; type = "branch"; branchId = "branch-evidence"; label = "Evidence path"; title = "Evidence-first branch"; x = 420; y = 180 },
          @{ id = "branch-readonly"; type = "branch"; branchId = "branch-readonly"; label = "Read-only path"; title = "Share boundary"; x = 430; y = 320 },
          @{ id = "branch-export"; type = "branch"; branchId = "branch-export"; label = "Export path"; title = "Replay capsule"; x = 420; y = 460 },
          @{ id = "demo-ready"; type = "convergence"; label = "Demo ready"; title = "Controlled external use"; x = 930; y = 310 }
        )
        edges = @(
          @{ id = "edge-root-evidence"; source = "root"; target = "branch-evidence"; branchId = "branch-evidence"; kind = "branch"; isHighlighted = $true },
          @{ id = "edge-root-readonly"; source = "root"; target = "branch-readonly"; branchId = "branch-readonly"; kind = "branch" },
          @{ id = "edge-root-export"; source = "root"; target = "branch-export"; branchId = "branch-export"; kind = "branch" },
          @{ id = "edge-evidence-ready"; source = "branch-evidence"; target = "demo-ready"; branchId = "branch-evidence"; kind = "convergence"; isHighlighted = $true }
        )
      }
      branches = @(
        @{ id = "branch-evidence"; title = "Evidence-first branch" },
        @{ id = "branch-readonly"; title = "Read-only share boundary" },
        @{ id = "branch-export"; title = "Evidence bundle capsule" }
      )
      evidenceRefs = @(
        @{ id = "ev-public-demo-doc"; title = "Public demo positioning"; sourceUri = "docs/product/public-demo.md"; lineStart = 1; summary = "Worldline is demoed as an evidence-backed OS." },
        @{ id = "ev-release-gate"; title = "Public demo release gate"; sourceUri = "src/services/worldline_release_gate_service.py"; lineStart = 1; summary = "Release gate verifies P5 share/export readiness." },
        @{ id = "ev-share-route"; title = "Read-only share route"; sourceUri = "web/src/views/worldline/WorldlinePublicShareView.vue"; lineStart = 1; summary = "Share view renders without write controls." }
      )
      wikiRefs = @(
        @{ id = "wiki-public-demo"; title = "Safe Public Demo" }
      )
      entityRefs = @(
        @{ id = "entity-public-demo-service"; name = "WorldlinePublicDemoService" },
        @{ id = "entity-read-only-share"; name = "ReadOnlyShareView" }
      )
      timelineRefs = @(
        @{ id = "tf-public-demo-freeze"; label = "Public demo dataset frozen for reproducible screenshots" }
      )
      replayCapsule = @{
        steps = @(
          "Open /worldline/share/demo-branch-evidence.",
          "Inspect branch evidence, wiki, graph, timeline, and quality refs.",
          "Export JSON or Markdown evidence bundle.",
          "Compare checksum before sharing externally."
        )
      }
    }
    bundlePreview = @{
      bundleId = "bundle-demo-branch-evidence"
      checksum = "sha256:static-qa"
      sections = @("evidence", "wiki", "entities", "timeline", "qualityGates")
      replayStepCount = 4
    }
    safety = @{ status = "passed"; secretViolations = @() }
  }
}

function Write-ApiResponse {
  param(
    [System.Net.HttpListenerContext]$Context,
    [string]$Path
  )
  switch -Wildcard ($Path) {
    "/api/system/info" {
      Write-Json $Context @{
        success = $true
        data = @{
          organization = @{ name = "Worldline"; logo = "/favicon.svg" }
          branding = @{ name = "Worldline"; title = "Worldline"; subtitle = "Public Demo" }
          themes = @()
          footer = @{ copyright = "Worldline 2026" }
        }
      }
      return
    }
    "/api/system/config" {
      Write-Json $Context @{}
      return
    }
    "/api/auth/me" {
      Write-Json $Context @{ id = 0; username = "public"; role = "guest" }
      return
    }
    "/api/worldline/public-demo/dataset" {
      $payload = New-SharePayload
      Write-Json $Context $payload.dataset
      return
    }
    "/api/worldline/public-demo/branches/*" {
      Write-Json $Context (New-SharePayload)
      return
    }
    "/api/worldline/public-demo/evidence-bundle" {
      if ($Context.Request.QueryString["format"] -eq "markdown") {
        Write-Text $Context "# bundle-demo-branch-evidence`n`n- Checksum: ``sha256:static-qa```n" "text/markdown; charset=utf-8"
      } else {
        Write-Json $Context @{ protocolVersion = "worldline-evidence-bundle-v0.1"; checksum = "sha256:static-qa" }
      }
      return
    }
    default {
      Write-Json $Context @{}
      return
    }
  }
}

function Write-SeedPage {
  param([System.Net.HttpListenerContext]$Context)
  $html = @"
<!doctype html>
<html>
<head><meta charset="utf-8"><title>P5 Public Demo QA Seed</title></head>
<body>
<script>
window.location.replace('/worldline/share/demo-branch-evidence?qaMetrics=1');
</script>
</body>
</html>
"@
  Write-Text -Context $Context -Text $html -ContentType "text/html; charset=utf-8"
}

function Add-QaInstrumentation {
  param([string]$Html)
  $script = @"
<script>
(function () {
  const params = new URLSearchParams(window.location.search);
  if (params.get('qaMetrics') !== '1') return;
  function writeMetrics() {
    const root = document.querySelector('[data-worldline-public-share="true"]');
    if (!root) return false;
    const exportButton = document.querySelector('[data-evidence-bundle-export="true"]');
    const dataset = document.querySelector('[data-public-demo-dataset="true"]');
    const clipped = [...root.querySelectorAll('button, a, strong, h1, h2, dd')]
      .map((node) => {
        const rect = node.getBoundingClientRect();
        return { text: (node.textContent || '').trim(), left: rect.left, right: rect.right, width: rect.width };
      })
      .filter((item) => item.right > window.innerWidth + 2 || item.left < -2);
    const payload = {
      path: window.location.pathname,
      sharePresent: true,
      datasetPresent: Boolean(dataset),
      bundleExportPresent: Boolean(exportButton),
      overflowX: document.documentElement.scrollWidth - window.innerWidth,
      clipped
    };
    let target = document.getElementById('qa-result');
    if (!target) {
      target = document.createElement('pre');
      target.id = 'qa-result';
      target.style.display = 'none';
      document.body.appendChild(target);
    }
    target.textContent = JSON.stringify(payload);
    return true;
  }
  let attempts = 0;
  const timer = setInterval(() => {
    attempts += 1;
    if (writeMetrics() || attempts > 60) clearInterval(timer);
  }, 250);
})();
</script>
"@
  return $Html -replace "</body>", "$script</body>"
}

function Write-StaticFile {
  param(
    [System.Net.HttpListenerContext]$Context,
    [string]$Path
  )
  $relative = $Path.TrimStart("/")
  if ([string]::IsNullOrWhiteSpace($relative)) {
    $relative = "index.html"
  }
  $candidate = [System.IO.Path]::GetFullPath([System.IO.Path]::Combine($distRoot, $relative))
  if (-not $candidate.StartsWith($distRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    Write-Text -Context $Context -Text "Not Found" -StatusCode 404
    return
  }
  if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
    $candidate = [System.IO.Path]::Combine($distRoot, "index.html")
  }
  if ([System.IO.Path]::GetFileName($candidate).ToLowerInvariant() -eq "index.html") {
    $html = [System.IO.File]::ReadAllText($candidate, [System.Text.Encoding]::UTF8)
    if ($Context.Request.Url.Query.Contains("qaMetrics=1")) {
      $html = Add-QaInstrumentation $html
    }
    Write-Text -Context $Context -Text $html -ContentType "text/html; charset=utf-8"
    return
  }
  $bytes = [System.IO.File]::ReadAllBytes($candidate)
  Write-Bytes -Context $Context -Bytes $bytes -ContentType (Get-ContentType $candidate)
}

$listener.Start()
Write-Host "P5_STATIC_READY $prefix"
try {
  while ($listener.IsListening) {
    $context = $listener.GetContext()
    try {
      $path = $context.Request.Url.AbsolutePath
      if ($path -eq "/qa-seed") {
        Write-SeedPage $context
      } elseif ($path.StartsWith("/api/")) {
        Write-ApiResponse -Context $context -Path $path
      } else {
        Write-StaticFile -Context $context -Path $path
      }
    } catch {
      Write-Text -Context $context -Text $_.Exception.Message -StatusCode 500
    }
  }
} finally {
  $listener.Stop()
  $listener.Close()
}
