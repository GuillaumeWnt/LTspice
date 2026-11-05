<#
.SYNOPSIS
    Synchronizes MCP servers from .agents/mcp_config.json to all AI environments.
.DESCRIPTION
    Source of Truth:
      - .agents/mcp_config.json (format: { "mcpServers": { ... } })

    Target Destinations:
      - .vscode/mcp.json             (VS Code format: { "servers": { ... }, "inputs": [ ... ] })
      - .mcp.json                    (Claude Code root standard)
      - .claude/mcp.json             (Claude directory standard)
      - .gemini/mcp_config.json      (Gemini workspace config)
      - .gemini/config/mcp_config.json (Antigravity config format)
#>

[CmdletBinding()]
param (
    [string]$SourceFile = ".agents/mcp_config.json"
)

$ErrorActionPreference = "Stop"

try {
    # 1. Verify and read source file
    if (-not (Test-Path $SourceFile)) {
        Write-Warning "Source file $SourceFile not found. Creating default empty structure."
        @{ mcpServers = @{} } | ConvertTo-Json -Depth 10 | Set-Content $SourceFile -Encoding UTF8
    }

    $rawContent = Get-Content -Path $SourceFile -Raw -Encoding UTF8
    $sourceData = $rawContent | ConvertFrom-Json

    if ($null -eq $sourceData.mcpServers) {
        $sourceData | Add-Member -MemberType NoteProperty -Name "mcpServers" -Value ([PSCustomObject]@{})
    }

    # 2. Build VS Code formatted configuration (.vscode/mcp.json)
    $vsCodeServers = [ordered]@{}
    foreach ($property in $sourceData.mcpServers.PSObject.Properties) {
        $name = $property.Name
        $config = $property.Value
        $entry = [ordered]@{}

        # Infer type: url -> http, command -> stdio
        if ($config.PSObject.Properties.Match('type').Count -gt 0) {
            $entry['type'] = $config.type
        } elseif ($config.PSObject.Properties.Match('url').Count -gt 0) {
            $entry['type'] = "http"
        } else {
            $entry['type'] = "stdio"
        }

        # Copy all other properties
        foreach ($p in $config.PSObject.Properties) {
            if ($p.Name -ne 'type') {
                $entry[$p.Name] = $p.Value
            }
        }
        $vsCodeServers[$name] = [PSCustomObject]$entry
    }

    # Preserve any existing user inputs in .vscode/mcp.json
    $inputs = @()
    if (Test-Path ".vscode/mcp.json") {
        try {
            $existingVsCode = (Get-Content ".vscode/mcp.json" -Raw -Encoding UTF8) | ConvertFrom-Json
            if ($null -ne $existingVsCode.inputs) {
                $inputs = $existingVsCode.inputs
            }
        } catch {}
    }

    $vsCodePayload = [ordered]@{
        servers = [PSCustomObject]$vsCodeServers
        inputs  = $inputs
    }
    $vsCodeJson = $vsCodePayload | ConvertTo-Json -Depth 10

    if (-not (Test-Path ".vscode")) { New-Item -ItemType Directory -Path ".vscode" -Force | Out-Null }
    [System.IO.File]::WriteAllText(".vscode/mcp.json", $vsCodeJson, [System.Text.Encoding]::UTF8)

    # 3. Build Standard mcpServers payload (Claude & Gemini)
    $standardPayload = [ordered]@{
        mcpServers = $sourceData.mcpServers
    }
    $standardJson = $standardPayload | ConvertTo-Json -Depth 10

    # Write .mcp.json (Root)
    [System.IO.File]::WriteAllText(".mcp.json", $standardJson, [System.Text.Encoding]::UTF8)

    # Write .claude/mcp.json
    if (-not (Test-Path ".claude")) { New-Item -ItemType Directory -Path ".claude" -Force | Out-Null }
    [System.IO.File]::WriteAllText(".claude/mcp.json", $standardJson, [System.Text.Encoding]::UTF8)

    # Write .gemini/mcp_config.json
    if (-not (Test-Path ".gemini")) { New-Item -ItemType Directory -Path ".gemini" -Force | Out-Null }
    [System.IO.File]::WriteAllText(".gemini/mcp_config.json", $standardJson, [System.Text.Encoding]::UTF8)

    # Write .gemini/config/mcp_config.json
    if (-not (Test-Path ".gemini/config")) { New-Item -ItemType Directory -Path ".gemini/config" -Force | Out-Null }
    [System.IO.File]::WriteAllText(".gemini/config/mcp_config.json", $standardJson, [System.Text.Encoding]::UTF8)

    Write-Host "[OK] MCP servers synchronized across .vscode, .claude, and .gemini from .agents/mcp_config.json." -ForegroundColor Green
} catch {
    Write-Error "Failed to synchronize MCP configurations: $_"
    exit 1
}

