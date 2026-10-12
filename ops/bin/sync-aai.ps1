<#
  sync-aai.ps1 - push selected project folders, with their git history, into one folder each
  of the private GitHub repo atompower4us/AAI.

  A source is a folder inside any local git repo (C:\Dev\own\MetaAtomic lives in the C:\Dev\own
  repo) or a repo root. Its history is extracted from a throwaway clone with git-filter-repo,
  so the source repo is never touched. Only COMMITTED work travels.

  The extract is deterministic: the same source history gives the same commit ids every run,
  so a re-sync merges only the new commits into AAI's main.

  Run:  powershell -NoProfile -File C:\Dev\ops\bin\sync-aai.ps1 MetaAtomic DeployFabric
        ... -List                      show what can be synced from C:\Dev\own
        ... C:\Dev\x\Repo=Repo2        any path; '=Name' sets the AAI folder (default: leaf name)
        ... -NoPush                    build the result locally, push nothing

  Back the other way (work done in AAI, e.g. a cloud session, on a branch):
        ... -Pull -Branch <aai-branch> MetaAtomic
      takes the commits on that branch since it left main that touch the folder, and applies them
      with git am -3 onto a NEW branch pull/<Name>-<aai-branch> in the source repo. Nothing is
      merged and nothing is pushed; on a conflict the am is aborted and the repo is left as it was.

  Needs: git, python with git-filter-repo (pip install git-filter-repo), gh logged in.
  Work dir: %LOCALAPPDATA%\aai-sync (script-owned; AAI clone is reset to origin each run).
#>
[CmdletBinding(PositionalBinding = $false)]
param(
    [Parameter(ValueFromRemainingArguments = $true)] [string[]] $Sources,
    [switch] $List,
    [switch] $NoPush,
    [switch] $Pull,
    [string] $Branch,
    [string] $Remote = 'https://github.com/atompower4us/AAI.git',
    [string] $Root = 'C:\Dev\own'
)
$ErrorActionPreference = 'Stop'

function Invoke-Git { & git.exe @args; if ($LASTEXITCODE -ne 0) { throw "git $($args -join ' ') failed" } }

if ($List -or -not $Sources) {
    Write-Host "Folders under $Root (pass one or more names):"
    Get-ChildItem $Root -Directory | Where-Object { $_.Name -notlike '.*' } | ForEach-Object { "  $($_.Name)" }
    if (-not $Sources) { exit 0 }
}

$work = Join-Path $env:LOCALAPPDATA 'aai-sync'
$aai = Join-Path $work 'AAI'
New-Item -ItemType Directory -Force $work | Out-Null

if (-not (Test-Path (Join-Path $aai '.git'))) {
    Invoke-Git clone -q $Remote $aai
}
Invoke-Git -C $aai fetch -q origin
$hasMain = (& git -C $aai ls-remote --heads origin main)
if ($hasMain) { Invoke-Git -C $aai checkout -q -B main origin/main }

if ($Pull) {
    if (-not $Branch) { throw '-Pull needs -Branch <aai-branch>' }
    & git -C $aai rev-parse -q --verify "refs/remotes/origin/$Branch" | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "no branch $Branch on $Remote" }
    foreach ($spec in $Sources) {
        $path, $target = $spec -split '=', 2
        if (-not [System.IO.Path]::IsPathRooted($path)) { $path = Join-Path $Root $path }
        $path = (Resolve-Path $path).Path
        if (-not $target) { $target = Split-Path $path -Leaf }
        $top = (& git -C $path rev-parse --show-toplevel)
        $prefix = (& git -C $path rev-parse --show-prefix)
        if ($prefix -and $prefix -ne "$target/") { throw "[$target] pull needs the AAI folder name to equal the source folder name" }
        if (& git -C $top status --porcelain) { throw "[$target] $top has uncommitted changes; commit or stash first" }

        $base = (& git -C $aai merge-base origin/main "origin/$Branch")
        $dir = Join-Path $work "pull-$target"
        if (Test-Path $dir) { Remove-Item -Recurse -Force $dir }
        New-Item -ItemType Directory -Force $dir | Out-Null
        Invoke-Git -C $aai format-patch -q -o $dir "$base..origin/$Branch" -- $target
        $patches = @(Get-ChildItem $dir -Filter '*.patch' | Sort-Object Name | ForEach-Object { $_.FullName })
        if (-not $patches) { Write-Host "[$target] nothing on $Branch touches $target since it left main"; continue }

        $was = (& git -C $top branch --show-current)
        $new = "pull/$target-$Branch"
        Invoke-Git -C $top switch -q -c $new
        $amArgs = @('-C', $top, 'am', '-3', '-q')
        if (-not $prefix) { $amArgs += '-p2' }
        & git.exe @amArgs @patches
        if ($LASTEXITCODE -ne 0) {
            & git -C $top am --abort
            & git -C $top switch -q $was
            & git -C $top branch -D $new | Out-Null
            throw "[$target] a patch did not apply; repo left on $was as it was"
        }
        Write-Host "[$target] $($patches.Count) commit(s) from $Branch applied on branch $new in $top (not merged)"
    }
    exit 0
}

foreach ($spec in $Sources) {
    $path, $target = $spec -split '=', 2
    if (-not [System.IO.Path]::IsPathRooted($path)) { $path = Join-Path $Root $path }
    $path = (Resolve-Path $path).Path
    if (-not $target) { $target = Split-Path $path -Leaf }

    $top = (& git -C $path rev-parse --show-toplevel)
    if ($LASTEXITCODE -ne 0) { throw "$path is not inside a git repo" }
    $prefix = (& git -C $path rev-parse --show-prefix)
    $dirty = (& git -C $path status --porcelain -- .)
    if ($dirty) { Write-Host "[$target] uncommitted changes in $path are NOT synced" }

    $tmp = Join-Path $work "src-$target"
    if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
    Invoke-Git clone -q --no-local --single-branch $top $tmp

    if ($prefix) {
        $filter = @('--path', $prefix)
        if ($prefix -ne "$target/") { $filter += @('--path-rename', "${prefix}:$target/") }
    } else {
        $filter = @('--to-subdirectory-filter', $target)
    }
    Push-Location $tmp
    try { & python -m git_filter_repo @filter --force --quiet; if ($LASTEXITCODE -ne 0) { throw "filter-repo failed for $target" } }
    finally { Pop-Location }

    Invoke-Git -C $aai fetch -q $tmp HEAD
    if (-not $hasMain -and -not (& git -C $aai rev-parse -q --verify HEAD)) {
        Invoke-Git -C $aai checkout -q -B main FETCH_HEAD
    } else {
        & git -C $aai merge -q --allow-unrelated-histories --no-edit -m "sync: $target" FETCH_HEAD
        if ($LASTEXITCODE -ne 0) { & git -C $aai merge --abort; throw "[$target] merge conflict - nothing pushed" }
    }
    Remove-Item -Recurse -Force $tmp
    Write-Host "[$target] $(& git -C $aai log -1 --format='%h %s' -- $target)"
}

if ($NoPush) { Write-Host "NoPush: result in $aai"; exit 0 }
Invoke-Git -C $aai push -q origin main
Write-Host "Pushed to $Remote (main $(& git -C $aai rev-parse --short HEAD))"
