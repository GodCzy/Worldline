param(
  [string]$DistPath = "D:\dev\Worldline\web\dist",
  [int]$Port = 5194
)

$ErrorActionPreference = "Stop"

$distRoot = [System.IO.Path]::GetFullPath($DistPath)
if (-not (Test-Path -LiteralPath $distRoot -PathType Container)) {
  throw "DistPath does not exist: $distRoot"
}
$logPath = [System.IO.Path]::GetFullPath([System.IO.Path]::Combine((Split-Path -Parent $PSCommandPath), "..", "p4-static-server-requests.log"))
"P4 static server started $(Get-Date -Format o)" | Set-Content -LiteralPath $logPath -Encoding UTF8

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
  $json = $Payload | ConvertTo-Json -Depth 20
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

function New-OperationalHealthPayload {
  @{
    status = "attention"
    service = "WorldlineOperationalHealthService"
    db_id = "kb_p4_demo"
    generated_at = "2026-06-14T22:00:00"
    queues = @{
      redis = @{ status = "available"; backend = "redis"; url = "redis://***" }
      knowledge_files = @{
        by_status = @{ error_parsing = 1; error_indexing = 1; queued = 1 }
        failed_count = 2
        active_count = 0
        recent_failed = @(
          @{ file_id = "file_parse_fail"; filename = "parse.pdf"; status = "error_parsing"; error_message = "parser failed" }
        )
      }
      workflow_runs = @{
        by_status = @{ failed = 1; queued = 1 }
        failed_count = 1
        active_count = 1
        recent = @(
          @{ workflow_id = "wfr_failed"; status = "failed"; step_tools = @("worldline.rebuild_wiki") }
        )
      }
    }
    failure_evidence = @{
      summary = @{
        total_failed_records = 3
        document_versions_failed = 1
        quality_gates_failed = 1
        workflow_runs_failed = 1
      }
      parsing = @{ failed_count = 1; recent = @() }
      indexing = @{ failed_count = 1; recent = @() }
      wiki_generation = @{ failed_count = 1; active_count = 0; recent = @(); retryable_statuses = @("error", "failed") }
      graph_rebuild = @{ failed_count = 0; active_count = 0; recent = @(); retryable_statuses = @("error", "failed") }
      quality_gates = @{ failed_count = 1; recent = @() }
    }
    retry_policy = @{ release_gate = "worldline_operational_readiness_contract"; stages = @{} }
    budgets = @{
      defaults = @{
        quality_gate_total_latency_ms = 5000
        quality_gate_estimated_usd = 0.1
        failed_file_count = 0
        failed_workflow_count = 0
      }
      observed = @{
        quality_gate_total_latency_ms = 9000
        quality_gate_estimated_usd = 0.25
        failed_file_count = 2
        failed_workflow_count = 1
      }
      violations = @(
        @{ metric = "quality_gate_total_latency_ms"; observed = 9000; budget = 5000 }
      )
      scopes = @{
        effective = @{
          kb = @{ failed_file_count = 0; failed_workflow_count = 0; active_workflow_count = 2 }
          run = @{ total_latency_ms = 600000; estimated_usd = 1.0 }
          branch = @{ generation_latency_ms = 15000; estimated_usd = 0.1 }
          gate = @{ total_latency_ms = 5000; estimated_usd = 0.1 }
        }
        observed = @{
          kb = @{ failed_file_count = 2; failed_workflow_count = 1; active_workflow_count = 1 }
          run = @{ total_latency_ms = 0; estimated_usd = 0 }
          branch = @{ generation_latency_ms = 0; estimated_usd = 0 }
          gate = @{ total_latency_ms = 9000; estimated_usd = 0.25 }
        }
        violations = @(
          @{ scope = "kb"; metric = "failed_file_count"; observed = 2; budget = 0 },
          @{ scope = "gate"; metric = "total_latency_ms"; observed = 9000; budget = 5000 }
        )
      }
    }
    cleanup_readiness = @{
      temporary_file_cleanup = "controlled_routine_available"
      deleted_kb_cleanup = "controlled_routine_available"
      minio_object_cleanup = "controlled_routine_available"
      archived_artifact_cleanup = "controlled_routine_available"
      blocked_by_active_workflows = $false
      action_endpoint = "/api/dashboard/worldline/operational-health/actions"
    }
    operation_controls = @{
      endpoint = "/api/dashboard/worldline/operational-health/actions"
      requires_admin = $true
      db_id_required = $true
      current_db_id = "kb_p4_demo"
      actions = @{
        requeue = @{ method = "POST"; dry_run_supported = $true }
        cleanup = @{ method = "POST"; dry_run_default = $true }
        update_budgets = @{ method = "POST"; scopes = @("branch", "gate", "kb", "run") }
        mark_source_stale = @{ method = "POST"; requires = @("asset_id or file_id or source_uri") }
      }
    }
    next_actions = @("review recent failure evidence and requeue through controlled service APIs")
  }
}

function Write-ApiResponse {
  param(
    [System.Net.HttpListenerContext]$Context,
    [string]$Path,
    [string]$Method
  )
  switch -Wildcard ($Path) {
    "/api/auth/me" {
      Write-Json $Context @{ id = 1; user_id = "qa_admin"; username = "qa_admin"; role = "admin"; phone_number = ""; avatar = ""; department_id = $null; department_name = "" }
      return
    }
    "/api/system/info" {
      Write-Json $Context @{
        success = $true
        data = @{
          organization = @{ name = "Worldline"; logo = "/favicon.svg"; avatar = "/avatar.jpg" }
          branding = @{ name = "Worldline"; title = "Worldline"; subtitle = "Operational QA"; description = "P4 static QA" }
          features = @()
          themes = @()
          actions = @()
          footer = @{ copyright = "Worldline 2026" }
        }
      }
      return
    }
    "/api/system/config" {
      Write-Json $Context @{}
      return
    }
    "/api/knowledge/databases" {
      Write-Json $Context @{ databases = @(@{ db_id = "kb_p4_demo"; database_id = "kb_p4_demo"; database_name = "P4 Demo KB"; name = "P4 Demo KB"; kb_type = "milvus"; created_at = "2026-06-14T22:00:00" }) }
      return
    }
    "/api/knowledge/databases/accessible" {
      Write-Json $Context @{ databases = @(@{ db_id = "kb_p4_demo"; name = "P4 Demo KB" }) }
      return
    }
    "/api/tasks" {
      Write-Json $Context @{ tasks = @(); summary = @{ total = 0; filtered_total = 0; status_counts = @{}; type_counts = @{} } }
      return
    }
    "/api/dashboard/worldline/operational-health" {
      Write-Json $Context (New-OperationalHealthPayload)
      return
    }
    "/api/dashboard/worldline/operational-health/actions" {
      Write-Json $Context @{
        operation_id = "ops_static_qa"
        action = "update_budgets"
        db_id = "kb_p4_demo"
        status = "dry_run"
        dry_run = $true
        audit = @{ recorded = $true; log_id = "audit_static_qa" }
      }
      return
    }
    "/api/dashboard/stats" {
      Write-Json $Context @{
        total_conversations = 42
        active_conversations = 7
        total_messages = 512
        total_users = 3
        feedback_stats = @{ total_feedbacks = 9; satisfaction_rate = 88 }
      }
      return
    }
    "/api/dashboard/stats/users" {
      Write-Json $Context @{ total_users = 3; active_users = 2; new_users = 1; users = @() }
      return
    }
    "/api/dashboard/stats/tools" {
      Write-Json $Context @{ total_calls = 12; tools = @() }
      return
    }
    "/api/dashboard/stats/knowledge" {
      Write-Json $Context @{ total_databases = 1; total_files = 3; databases = @() }
      return
    }
    "/api/dashboard/stats/agents" {
      Write-Json $Context @{ total_agents = 1; active_agents = 1; agents = @() }
      return
    }
    "/api/dashboard/stats/calls/timeseries" {
      Write-Json $Context @{
        categories = @("worldline")
        data = @(
          @{ date = "2026-06-12"; data = @{ worldline = 3 } },
          @{ date = "2026-06-13"; data = @{ worldline = 5 } },
          @{ date = "2026-06-14"; data = @{ worldline = 7 } }
        )
      }
      return
    }
    "/api/dashboard/conversations" {
      Write-Json $Context @(
        @{ thread_id = "qa-thread"; title = "P4 operational QA"; user_id = "qa_admin"; message_count = 5; status = "active"; updated_at = "2026-06-14T22:00:00" }
      )
      return
    }
    "/api/chat/default_agent" {
      Write-Json $Context @{ default_agent_id = "worldline-agent" }
      return
    }
    "/api/chat/agent/*/configs/*" {
      Write-Json $Context @{ config = @{ id = "default"; name = "Default"; is_default = $true; config_json = @{ context = @{} } } }
      return
    }
    "/api/chat/agent/*/configs" {
      Write-Json $Context @{ configs = @(@{ id = "default"; name = "Default"; is_default = $true; config_json = @{ context = @{} } }) }
      return
    }
    "/api/chat/agent/*" {
      Write-Json $Context @{ id = "worldline-agent"; name = "Worldline Agent"; configurable_items = @{} }
      return
    }
    "/api/chat/agent" {
      Write-Json $Context @{ agents = @(@{ id = "worldline-agent"; name = "Worldline Agent"; description = "Static QA agent" }) }
      return
    }
    "/api/chat/agent*" {
      Write-Json $Context @{ agents = @(@{ id = "worldline-agent"; name = "Worldline Agent"; description = "Static QA agent" }) }
      return
    }
    "/api/mcp*" {
      Write-Json $Context @{ data = @() }
      return
    }
    "/api/skills*" {
      Write-Json $Context @{ data = @() }
      return
    }
    default {
      if ($Method -eq "GET") {
        Write-Json $Context @{}
      } else {
        Write-Json $Context @{ success = $true }
      }
      return
    }
  }
}

function Write-SeedPage {
  param([System.Net.HttpListenerContext]$Context)
  $drawer = $Context.Request.QueryString["drawer"]
  $target = "/dashboard?qaMetrics=1"
  if (-not [string]::IsNullOrWhiteSpace($drawer)) {
    $target = "/dashboard?qaMetrics=1&qaDrawer=$([System.Uri]::EscapeDataString($drawer))"
  }
  $html = @"
<!doctype html>
<html>
<head><meta charset="utf-8"><title>P4 Dashboard QA Seed</title></head>
<body>
<script>
localStorage.setItem('user_token', 'qa-admin-token');
localStorage.setItem('worldline_app_nav_expanded', '1');
window.location.replace('$target');
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
  const drawerAction = params.get('qaDrawer') || '';
  let clicked = false;
  function ensureDrawer() {
    if (!drawerAction || clicked) return;
    const buttons = [...document.querySelectorAll('.worldline-ops-controls button')];
    const target = buttons.find((button) => button.textContent.includes('\u9884\u7b97')) || buttons[3] || buttons.at(-1);
    if (target) {
      target.click();
      clicked = true;
    }
  }
  function writeMetrics() {
    const panel = document.querySelector('[data-worldline-p4-ops-panel="true"]');
    if (!panel) return false;
    ensureDrawer();
    const drawer = document.querySelector('[data-worldline-p4-action-drawer="true"]');
    if (drawer) {
      const wrapper = drawer.closest('.ant-drawer-content-wrapper');
      if (wrapper) {
        wrapper.style.transition = 'none';
        wrapper.style.transform = 'none';
        wrapper.style.right = '0';
      }
    }
    const panelRect = panel.getBoundingClientRect();
    const clipped = [...panel.querySelectorAll('button, input, strong, span, p')]
      .map((node) => {
        const rect = node.getBoundingClientRect();
        return {
          text: (node.textContent || node.getAttribute('placeholder') || '').trim(),
          left: rect.left,
          right: rect.right,
          width: rect.width
        };
      })
      .filter((item) => item.right > window.innerWidth + 2 || item.left < -2);
    const payload = {
      path: window.location.pathname,
      panelPresent: true,
      drawerPresent: Boolean(drawer),
      statusText: panel.querySelector('.worldline-ops-head .ant-tag')?.textContent?.trim() || '',
      metrics: [...panel.querySelectorAll('.worldline-ops-metrics strong')].map((node) => node.textContent.trim()),
      nextAction: panel.querySelector('.worldline-ops-next')?.textContent?.trim() || '',
      overflowX: document.documentElement.scrollWidth - window.innerWidth,
      clipped,
      panelRect: { left: panelRect.left, top: panelRect.top, width: panelRect.width, height: panelRect.height }
    };
    let target = document.getElementById('qa-result');
    if (!target) {
      target = document.createElement('pre');
      target.id = 'qa-result';
      target.style.display = 'none';
      document.body.appendChild(target);
    }
    target.textContent = JSON.stringify(payload);
    return !drawerAction || Boolean(drawer);
  }
  let attempts = 0;
  const timer = setInterval(() => {
    attempts += 1;
    if (writeMetrics() || attempts > 60) {
      clearInterval(timer);
    }
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
Write-Host "P4_STATIC_READY $prefix"
try {
  while ($listener.IsListening) {
    $context = $listener.GetContext()
    try {
      $path = $context.Request.Url.AbsolutePath
      $method = $context.Request.HttpMethod
      "$method $path $($context.Request.Url.Query)" | Add-Content -LiteralPath $logPath -Encoding UTF8
      if ($path -eq "/qa-seed") {
        Write-SeedPage $context
      } elseif ($path.StartsWith("/api/")) {
        Write-ApiResponse -Context $context -Path $path -Method $method
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
