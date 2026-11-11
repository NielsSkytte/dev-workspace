# Starts an agent CLI from Zed in the project root of the active file.
# Project root = nearest folder at or above the start folder that holds a CLAUDE.md,
# stopping at C:\Dev. Called by the tasks in %APPDATA%\Zed\tasks.json.
param(
    [Parameter(Mandatory = $true)][ValidateSet('claude', 'claude-priv', 'gemini', 'antigravity')][string]$Agent,
    [string]$FileDir = 'none',
    [string]$WorktreeRoot = 'C:\Dev'
)

$devRoot = 'C:\Dev'
$start = if ($FileDir -and $FileDir -ne 'none' -and (Test-Path $FileDir)) { $FileDir } else { $WorktreeRoot }
$dir = (Resolve-Path $start).Path.TrimEnd('\')

$root = $null
if ($dir -like "$devRoot*") {
    $probe = $dir
    while ($probe -and $probe.Length -ge $devRoot.Length) {
        if (Test-Path (Join-Path $probe 'CLAUDE.md')) { $root = $probe; break }
        $probe = Split-Path $probe -Parent
    }
}
if (-not $root) { $root = $dir }

Set-Location $root
Write-Host "[$Agent] $root"

switch ($Agent) {
    'claude'      { & claude }
    'claude-priv' { & claude-priv }
    'gemini'      { & gemini }
    'antigravity' { & "$env:LOCALAPPDATA\Programs\Antigravity IDE\bin\antigravity-ide.cmd" $root }
}
