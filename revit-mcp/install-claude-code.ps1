<#
.SYNOPSIS
Install the Revit MCP add-in + server for these Claude Code agents (Revit 2025).

.DESCRIPTION
Run it with Revit closed (double-click Install.cmd next to this file). It:
  1. Deploys the Revit 2025 add-in and installs the MCP server to
     %LOCALAPPDATA%\RevitMCPServer, using install.ps1 from this folder
     (needs Node.js 18+ on PATH; runs npm install there).
  2. Adds the "revit-2025" server to .mcp.json in the workspace folder (the
     parent of this folder), backing up an existing .mcp.json and keeping any
     other servers in it. The server must be named "revit-2025": the agents'
     tools are called mcp__revit-2025__*.

Run it again after every `git pull` that changed revit-mcp/ (see VERSION.txt).

.PARAMETER Workspace
Folder whose .mcp.json is written. Default: the folder above revit-mcp.

.PARAMETER SkipRevitCheck
Do not refuse to run while Revit is open (testing only).
#>
param(
    [string]$Workspace = (Split-Path $PSScriptRoot -Parent),
    [switch]$SkipRevitCheck
)

$ErrorActionPreference = "Stop"
function Info($m) { Write-Host $m -ForegroundColor Cyan }
function Good($m) { Write-Host "  OK  $m" -ForegroundColor Green }
function Fail($m) { Write-Host "  !!  $m" -ForegroundColor Red; exit 1 }

if (-not $SkipRevitCheck -and (Get-Process Revit -ErrorAction SilentlyContinue)) {
    Fail "Revit is running. Close every Revit window, then run this again."
}
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Fail "Node.js was not found. Install the LTS version from https://nodejs.org, then run this again."
}

Info "Installing the Revit 2025 add-in and the MCP server"
& (Join-Path $PSScriptRoot "install.ps1") -RevitVersions 2025 -NoClientConfig | Out-Host
if (-not $?) { Fail "install.ps1 failed - see the messages above." }

$index = Join-Path $env:LOCALAPPDATA "RevitMCPServer\dist\index.js"
if (-not (Test-Path $index)) { Fail "MCP server not found at $index." }
if (-not (Test-Path (Join-Path $env:LOCALAPPDATA "RevitMCPServer\node_modules"))) {
    Fail "npm install did not run in $env:LOCALAPPDATA\RevitMCPServer. Run 'npm install --production' there."
}

Info "Writing .mcp.json for Claude Code"
$mcpPath = Join-Path $Workspace ".mcp.json"
$config = [pscustomobject]@{ mcpServers = [pscustomobject]@{} }
if (Test-Path $mcpPath) {
    Copy-Item $mcpPath "$mcpPath.bak-$(Get-Date -Format yyyyMMdd-HHmmss)" -Force
    try { $config = Get-Content $mcpPath -Raw | ConvertFrom-Json }
    catch { Fail "$mcpPath is not valid JSON - fix or delete it, then run this again." }
    if (-not $config.PSObject.Properties["mcpServers"]) {
        $config | Add-Member -NotePropertyName mcpServers -NotePropertyValue ([pscustomobject]@{})
    }
}
$entry = [pscustomobject]@{
    command = "node"
    args    = @($index -replace '\\', '/')
    env     = [pscustomobject]@{ REVIT_MCP_VERSION = "2025"; REVIT_MCP_PORT = "7891" }
}
$config.mcpServers | Add-Member -NotePropertyName "revit-2025" -NotePropertyValue $entry -Force

# Windows PowerShell 5.1 writes a one-element array as a plain string; put the brackets back.
$json = $config | ConvertTo-Json -Depth 8
$json = [regex]::Replace($json, '("args":\s*)"([^"]*)"', '$1["$2"]')
[System.IO.File]::WriteAllText($mcpPath, $json, (New-Object System.Text.UTF8Encoding($false)))
Good "$mcpPath -> revit-2025"

Write-Host ""
Info "Done. Next:"
Write-Host "  1. Start Revit 2025 and open a project (one Revit only)."
Write-Host "  2. Start Claude Code in $Workspace and approve the 'revit-2025' server when asked."
Write-Host "  3. Say: Let's start with Revit_Guide"
