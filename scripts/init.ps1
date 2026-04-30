# Worldline Initialization Script for PowerShell
# This script helps set up the local Worldline development environment.
# Note: API keys will be visible during input.

Write-Host "Initializing Worldline project..." -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

if (Test-Path ".env") {
    Write-Host ".env file already exists. Skipping environment setup." -ForegroundColor Green
} else {
    Write-Host ".env file not found. Starting environment setup." -ForegroundColor Yellow
    Write-Host ""

    Write-Host "SiliconFlow API Key required" -ForegroundColor Yellow
    Write-Host "Get your API key from: https://cloud.siliconflow.cn/" -ForegroundColor Blue
    Write-Host "Press Ctrl+C at any time to cancel." -ForegroundColor Gray
    Write-Host ""

    do {
        $apiKey = Read-Host "Please enter your SILICONFLOW_API_KEY"
        if ([string]::IsNullOrEmpty($apiKey)) {
            Write-Host "API Key cannot be empty. Please try again." -ForegroundColor Red
        }
    } while ([string]::IsNullOrEmpty($apiKey))

    Write-Host ""
    Write-Host "Tavily API Key (optional) - for search service" -ForegroundColor Yellow
    Write-Host "Get your API key from: https://app.tavily.com/" -ForegroundColor Blue

    $TAVILY_API_KEY = Read-Host "Please enter your TAVILY_API_KEY (press Enter to skip)"

    $envContent = @"
# SiliconFlow API Key (required)
SILICONFLOW_API_KEY=$apiKey

# Tavily API Key (optional - for search service)
"@

    if (-not [string]::IsNullOrEmpty($TAVILY_API_KEY)) {
        $envContent += "`nTAVILY_API_KEY=$TAVILY_API_KEY"
    }

    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host ".env file created successfully." -ForegroundColor Green

    Remove-Variable -Name "apiKey" -ErrorAction SilentlyContinue
    Remove-Variable -Name "TAVILY_API_KEY" -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "Pulling Docker images..." -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan

$images = @(
    "python:3.12-slim",
    "node:20-slim",
    "node:20-alpine",
    "milvusdb/milvus:v2.5.6",
    "neo4j:5.26",
    "minio/minio:RELEASE.2023-03-20T20-16-18Z",
    "ghcr.io/astral-sh/uv:0.7.2",
    "nginx:alpine",
    "quay.io/coreos/etcd:v3.5.5",
    "postgres:16"
)

foreach ($image in $images) {
    Write-Host "Pulling ${image}..." -ForegroundColor Yellow
    try {
        & docker/pull_image.ps1 $image
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Successfully pulled ${image}" -ForegroundColor Green
        } else {
            Write-Host "Failed to pull ${image}" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "Error pulling ${image}: $_" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Initialization complete." -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green
Write-Host "You can now run: docker compose up -d --build" -ForegroundColor Cyan
Write-Host "This starts the local Worldline development stack." -ForegroundColor Cyan
