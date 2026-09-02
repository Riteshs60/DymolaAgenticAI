# Install Dymola Agentic AI skills into Claude Code (Windows)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$DestRoot = Join-Path $env:USERPROFILE ".claude\skills"

$Copy = $false
if ($args -contains "-Copy") { $Copy = $true }

New-Item -ItemType Directory -Force -Path $DestRoot | Out-Null

$items = @(
  "scripts",
  "validate-dymola",
  "simulate-dymola",
  "expose-encrypted-params",
  "inspect-dymosim",
  "tune-parameters",
  "diagnose-dymola",
  "edit-modelica-dymola",
  "dymola-model-architecture"
)

foreach ($name in $items) {
  $src = Join-Path $Root $name
  $dst = Join-Path $DestRoot $name
  if (-not (Test-Path $src)) {
    Write-Warning "Missing $src — skip"
    continue
  }
  if (Test-Path $dst) {
    Remove-Item -Recurse -Force $dst
  }
  if ($Copy) {
    Copy-Item -Recurse $src $dst
    Write-Host "Copied $name"
  } else {
    New-Item -ItemType Junction -Path $dst -Target $src | Out-Null
    Write-Host "Linked $name"
  }
}

Write-Host ""
Write-Host "Done. Start a new Claude Code session and ask it to list Dymola skills."
Write-Host "Scripts dir should resolve as ../scripts from each skill."
