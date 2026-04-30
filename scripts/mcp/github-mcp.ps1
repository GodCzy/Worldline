$ErrorActionPreference = "Stop"

$token = (gh auth token).Trim()
if ([string]::IsNullOrWhiteSpace($token)) {
  throw "GitHub MCP 启动失败：未获取到 gh 登录令牌。请先执行 gh auth login。"
}

$env:GITHUB_PERSONAL_ACCESS_TOKEN = $token
$env:GITHUB_READ_ONLY = "1"
$env:GITHUB_TOOLSETS = "default,actions"

docker run -i --rm `
  -e GITHUB_PERSONAL_ACCESS_TOKEN `
  -e GITHUB_READ_ONLY `
  -e GITHUB_TOOLSETS `
  ghcr.io/github/github-mcp-server
