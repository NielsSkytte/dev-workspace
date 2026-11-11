# Starts an agent CLI from Zed in the project root of the active file.
# Project root = nearest folder at or above the active file that holds a CLAUDE.md,
# stopping at C:\Dev. Zed passes only the open file, never a folder selected in the
# file tree, so when no open file points to a project the script lists the projects
# and asks which one. Called by the tasks in %APPDATA%\Zed\tasks.json.
param(
    [Parameter(Mandatory = $true)][ValidateSet('claude', 'claude-priv', 'gemini', 'antigravity')][string]$Agent,
    [string]$FilePath = 'none',
    [string]$WorktreeRoot = 'C:\Dev'
)

$devRoot = 'C:\Dev'
$start = $WorktreeRoot
if ($FilePath -and $FilePath -ne 'none' -and (Test-Path $FilePath)) {
    $start = if (Test-Path $FilePath -PathType Container) { $FilePath } else { Split-Path $FilePath -Parent }
}
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

if ($root -eq $devRoot) {
    # Projects = folders with a CLAUDE.md under customers\ and own\ (dot-folders skipped).
    $projects = @(Get-ChildItem "$devRoot\customers", "$devRoot\own" -Filter CLAUDE.md -Recurse -Depth 2 -File -ErrorAction SilentlyContinue |
        ForEach-Object { $_.DirectoryName } |
        Where-Object { $_ -notmatch '\\\.' } |
        Sort-Object -Unique)
    Write-Host "[$Agent] Pick a project:"
    Write-Host ("  {0,2}  {1}" -f 0, 'C:\Dev (workspace)')
    for ($i = 0; $i -lt $projects.Count; $i++) {
        Write-Host ("  {0,2}  {1}" -f ($i + 1), $projects[$i].Substring($devRoot.Length + 1))
    }
    $pick = Read-Host 'Number (Enter = 0)'
    $n = 0
    if ([int]::TryParse($pick, [ref]$n) -and $n -ge 1 -and $n -le $projects.Count) { $root = $projects[$n - 1] }
}

Set-Location $root
Write-Host "[$Agent] $root"

switch ($Agent) {
    'claude'      { & claude }
    'claude-priv' { & claude-priv }
    'gemini'      { & gemini }
    'antigravity' { & "$env:LOCALAPPDATA\Programs\Antigravity IDE\bin\antigravity-ide.cmd" $root }
}
