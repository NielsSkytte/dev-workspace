<#
  own-status.ps1 - read-only state of C:\Dev\own against the private GitHub repo atompower4us/AAI.
  Prints facts, changes nothing (it only fetches into the script-owned clone from sync-aai.ps1).

  Per folder that exists in both own and AAI:
    IN SYNC   the tree of own HEAD:<folder> equals AAI main:<folder>
    BEHIND    own has committed work AAI main does not hold (the post-commit hook should have pushed it)
    UNCOMMITTED  files in the folder are modified; they never travel
  Per AAI branch other than main:
    PENDING   commits on it whose patch is not on main (git cherry). A signal only: it also counts
              files outside own's folders; sync-aai.ps1 -Pull -Branch <branch> <Folder> is the arbiter.

  Run:  powershell -NoProfile -File C:\Dev\ops\bin\own-status.ps1
#>
[CmdletBinding()]
param(
    [string] $Root = 'C:\Dev\own',
    [string] $Remote = 'https://github.com/atompower4us/AAI.git'
)
$ErrorActionPreference = 'Stop'
$aai = Join-Path $env:LOCALAPPDATA 'aai-sync\AAI'
if (-not (Test-Path (Join-Path $aai '.git'))) {
    New-Item -ItemType Directory -Force (Split-Path $aai) | Out-Null
    & git.exe clone -q $Remote $aai
}
& git.exe -C $aai fetch -q origin

$top = (& git.exe -C $Root rev-parse --show-toplevel)
Write-Host "repo     $top  branch $(& git.exe -C $Root branch --show-current)"
$hook = Join-Path $top '.git\hooks\post-commit'
if (Test-Path $hook) {
    $m = Select-String -Path $hook -Pattern '^FOLDERS="(.*)"' | Select-Object -First 1
    $hooked = if ($m) { $m.Matches[0].Groups[1].Value } else { '?' }
    Write-Host "hook     post-commit installed, pushes: $hooked"
} else {
    Write-Host "hook     NOT installed: AAI only changes when sync-aai.ps1 is run by hand"
    $hooked = ''
}

$aaiFolders = @(& git.exe -C $aai ls-tree --name-only -d origin/main)
$ownFolders = @(Get-ChildItem $Root -Directory | Where-Object { $_.Name -notlike '.*' } | ForEach-Object { $_.Name })
foreach ($f in ($ownFolders | Sort-Object)) {
    $inAai = $aaiFolders -contains $f
    $hookedHere = (" $hooked ") -match " $f "
    $dirty = @(& git.exe -C $Root status --porcelain -- $f).Count
    $line = "{0,-16}" -f $f
    if (-not $inAai) {
        $line += "not in AAI" + $(if ($hookedHere) { " (hooked: first commit creates it)" } else { " (add to FOLDERS in the hook, or run sync-aai.ps1 $f)" })
    } else {
        $a = (& git.exe -C $Root rev-parse "HEAD:$f" 2>$null)
        $b = (& git.exe -C $aai rev-parse "origin/main:$f" 2>$null)
        $line += $(if ($a -eq $b) { "IN SYNC" } else { "BEHIND (committed in own, not in AAI main)" })
        if (-not $hookedHere) { $line += "; not hooked" }
    }
    if ($dirty) { $line += "; UNCOMMITTED $dirty file(s)" }
    Write-Host $line
}

foreach ($f in $aaiFolders) {
    if ($ownFolders -notcontains $f -and $f -notlike '.*') { Write-Host ("{0,-16}AAI only (lives in AAI, no folder in own)" -f $f) }
}

foreach ($b in (& git.exe -C $aai branch -r --format='%(refname:short)' | Where-Object { $_ -notmatch '/(main|HEAD)$' -and $_ -ne 'origin' })) {
    $pending = @(& git.exe -C $aai cherry origin/main $b | Where-Object { $_ -like '+*' })
    if ($pending.Count) {
        $touch = @(& git.exe -C $aai diff --name-only "origin/main...$b" | ForEach-Object { ($_ -split '/')[0] } | Sort-Object -Unique)
        Write-Host ("branch   {0}: PENDING {1} commit(s) touching {2}" -f $b, $pending.Count, ($touch -join ', '))
    }
}
