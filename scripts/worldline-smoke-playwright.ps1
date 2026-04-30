param(
  [string]$BaseUrl = "http://127.0.0.1:5173",
  [string]$OutDir = "D:\worldline\artifacts\playwright-smoke"
)

$ErrorActionPreference = "Stop"

Write-Host "[worldline-smoke] ensure output dir: $OutDir"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Write-Host "[worldline-smoke] install browsers (chromium + webkit)"
npx -y playwright@1.55.0 install chromium webkit | Out-Host

Write-Host "[worldline-smoke] desktop captures"
npx -y playwright@1.55.0 screenshot --full-page --wait-for-timeout 1200 "$BaseUrl/worldline?cb=desktop" "$OutDir/desktop-worldline.png" | Out-Host
npx -y playwright@1.55.0 screenshot --full-page --wait-for-timeout 1200 "$BaseUrl/worldline/poe?cb=desktop" "$OutDir/desktop-worldline-poe.png" | Out-Host
npx -y playwright@1.55.0 screenshot --full-page --wait-for-timeout 1200 "$BaseUrl/worldline/unknown?cb=desktop" "$OutDir/desktop-worldline-unknown.png" | Out-Host

Write-Host "[worldline-smoke] fresh-user-data capture (incognito-equivalent)"
$tmpUser = Join-Path $OutDir "tmp-user"
npx -y playwright@1.55.0 screenshot --user-data-dir "$tmpUser" --full-page --wait-for-timeout 1200 "$BaseUrl/worldline?cb=fresh" "$OutDir/fresh-worldline.png" | Out-Host

Write-Host "[worldline-smoke] mobile captures (iPhone 12)"
npx -y playwright@1.55.0 screenshot --device "iPhone 12" --full-page --wait-for-timeout 1200 "$BaseUrl/worldline/poe?cb=mobile" "$OutDir/mobile-worldline-poe.png" | Out-Host
npx -y playwright@1.55.0 screenshot --device "iPhone 12" --full-page --wait-for-timeout 1200 "$BaseUrl/worldline/unknown?cb=mobile" "$OutDir/mobile-worldline-unknown.png" | Out-Host

Write-Host "[worldline-smoke] done"
Write-Host "Artifacts: $OutDir"
