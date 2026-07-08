#requires -Version 5.1
<#
  heal-repos.ps1 - idempotent harness/backup wiring for the two-tier repo model.

  Model:
    C:\Dev                      = 'dev' repo (harness/ops); ignores /customers/ and /own/
    C:\Dev\customers\<Customer> = one LOCAL repo per customer (backup + privacy unit)
    C:\Dev\own                  = one LOCAL repo (same role)
    <unit>\<project>            = LOCAL project  (plain folder, tracked by the unit repo)
                                  or DEVOPS project (its own repo w/ remote): the unit repo ignores
                                  its CONTENTS but backs up its internal metadata (CLAUDE.md,
                                  CONTEXT.md, CONTEXT_*.md, INBOX.md) via hard links in
                                  <unit>\.project-meta\<sub>\ - code lives in DevOps, context
                                  lives in the personal unit repo (decided 2026-07-06)

  For every repo unit (each customers\* dir, plus own) this ensures:
    1. git init if it is not yet a repo
    2. detect nested git repos at both storage-standard depths (AGENTS.md > Conventions >
       Storage standard): flat under the unit (grandfathered), or role-named inside a project
       folder (<unit>\<project>\<role>, e.g. fabric/, infra/, wiki/) -> ignore them, and classify
       each by its 'origin' remote against ops/config/internal-remotes.txt: internal/personal
       (GitHub, PingalaGlobal) = ignored only; customer-facing (any other remote) = ignored AND
       guarded; no-remote nested repo = flagged (fold it in, or give it a remote)
    3. a harness-managed block in .gitignore (.claude, venvs, detected sub-repos)
    4. the harness link: <unit>\.claude\{commands,skills} -> C:\Dev\.claude\{...} (dir junctions)
       plus <unit>\.claude\settings.json hard-linked to C:\Dev\.claude\settings.json (no elevation)
       so the SessionStart/Stop/UserPromptSubmit hooks (memory capture + time tracking) load every session
    5. for each DevOps (customer-facing) sub-repo: link the harness there too, and add the
       internal-only harness names (.claude/, CLAUDE.md, CONTEXT.md, CONTEXT_*.md, INBOX.md) to its
       .git\info\exclude (LOCAL) so internal info can never be committed to the customer's repo.
       Only harness-reserved names are excluded; generic doc folders (decisions/, architecture/)
       are left alone so legitimate customer-facing docs still commit. The real guarantee is
       structural: internal info lives OUTSIDE the code repo (parent/sibling), never inside it.
    6. an initial commit only if the unit repo has no commits yet

  Safe to run repeatedly. No remotes are touched. No files are deleted.

  Usage:
    powershell -File ops\bin\heal-repos.ps1            # heal every unit
    powershell -File ops\bin\heal-repos.ps1 -Only C:\Dev\customers\NewCustomer
#>
[CmdletBinding()]
param(
  [string]$Dev = "C:\Dev",
  [string]$Only
)

$ErrorActionPreference = "Stop"
$src = Join-Path $Dev ".claude"
$beg = "# >>> harness-managed (heal-repos.ps1) >>>"
$end = "# <<< harness-managed <<<"

# Internal remote allowlist (substrate config). A nested repo whose origin URL matches any
# pattern here is internal/personal (safe to hold everything); anything else with a remote is
# treated as customer-facing. Missing file -> empty list -> everything-with-a-remote is customer.
$internalCfg = Join-Path $Dev "ops\config\internal-remotes.txt"
$internalPatterns = @()
if (Test-Path $internalCfg) {
  $internalPatterns = Get-Content $internalCfg |
    Where-Object { $_ -and $_ -notmatch '^\s*#' } | ForEach-Object { $_.Trim() }
}

function New-JunctionIfMissing($linkDir, $name) {
  $link = Join-Path $linkDir $name
  if (-not (Test-Path $link)) {
    New-Item -ItemType Junction -Path $link -Target (Join-Path $src $name) | Out-Null
    return $true
  }
  return $false
}

function New-FileLinkIfMissing($linkDir, $name) {
  # Junctions only work on directories; a single file (settings.json) needs a link.
  # Use a HARD link (NTFS, same volume, no elevation needed) so the harness hooks config is
  # shared byte-for-byte and the SessionStart/Stop/UserPromptSubmit hooks (memory capture +
  # time tracking) load in every unit session. C:\Dev\.claude\settings.json stays the source.
  $link = Join-Path $linkDir $name
  $tgt = Join-Path $src $name
  if (Test-Path $link) {
    # self-heal: if an atomic-save broke the hard link and content diverged, relink
    if ((Get-FileHash $link).Hash -eq (Get-FileHash $tgt).Hash) { return $false }
    Remove-Item $link -Force
  }
  New-Item -ItemType HardLink -Path $link -Target $tgt | Out-Null
  return $true
}

function Link-Harness($root) {
  $dc = Join-Path $root ".claude"
  if (-not (Test-Path $dc)) { New-Item -ItemType Directory -Path $dc | Out-Null }
  $a = New-JunctionIfMissing $dc "commands"
  $b = New-JunctionIfMissing $dc "skills"
  $c = New-FileLinkIfMissing $dc "settings.json"
  return ($a -or $b -or $c)
}

function Ensure-Excludes($repo) {
  # Local ignore (never committed) so a customer-facing DevOps repo can NEVER carry
  # internal-only harness files, even if one is accidentally created inside it.
  $patterns = @(".claude/", "CLAUDE.md", "CONTEXT.md", "CONTEXT_*.md", "INBOX.md")
  $ex = Join-Path $repo ".git\info\exclude"
  if (-not (Test-Path $ex)) { return }
  $existing = Get-Content $ex
  foreach ($p in $patterns) {
    if (-not ($existing | Where-Object { $_ -eq $p })) { Add-Content -Path $ex -Value $p -Encoding utf8 }
  }
}

function Get-RemoteClass($repo) {
  # 'internal' | 'customer' | 'none' based on the origin remote vs the internal allowlist.
  # List remotes first (silent) so a repo with no 'origin' never emits stderr, which under
  # $ErrorActionPreference='Stop' would otherwise abort the run.
  if (@(git -C $repo remote 2>$null) -notcontains "origin") { return "none" }
  $url = git -C $repo remote get-url origin 2>$null
  if (-not $url) { return "none" }
  foreach ($p in $internalPatterns) { if ($url -like "*$p*") { return "internal" } }
  return "customer"
}

function Get-SubRepos($unit) {
  # Nested-repo discovery per the storage standard: a code repo sits either directly under the
  # unit (grandfathered flat repos) or one level deeper, role-named inside a project folder.
  # Two levels only; never descends INTO a found repo, and skips harness/meta dirs by name so
  # the .claude junction is never traversed. Rel = unit-relative path, forward slashes.
  $skip = @(".claude", ".project-meta", ".git", ".vscode")
  $found = @()
  foreach ($child in (Get-ChildItem $unit -Directory -Force | Where-Object { $skip -notcontains $_.Name })) {
    if (Test-Path (Join-Path $child.FullName ".git")) {
      $found += [pscustomobject]@{ Dir = $child; Rel = $child.Name }
      continue
    }
    foreach ($gc in (Get-ChildItem $child.FullName -Directory -Force | Where-Object { $skip -notcontains $_.Name })) {
      if (Test-Path (Join-Path $gc.FullName ".git")) {
        $found += [pscustomobject]@{ Dir = $gc; Rel = ($child.Name + "/" + $gc.Name) }
      }
    }
  }
  return @($found)
}

function Set-ManagedIgnore($unit, $subrepos) {
  $giPath = Join-Path $unit ".gitignore"
  $block = @($beg,
    "# Harness junction -> $src (never track or traverse)",
    ".claude/",
    "",
    "# Environments (regenerable)",
    "**/venv/", "**/.venv/", "__pycache__/")
  if ($subrepos.Count -gt 0) {
    $block += ""
    $block += "# Nested project repos with their own remote (DevOps/wiki): code backed up there, not here."
    $block += "# Their internal metadata (CLAUDE/CONTEXT/INBOX) IS backed up here - hard-linked into"
    $block += "# .project-meta/<sub>/ (tracked), since git refuses paths inside a nested repo."
    foreach ($s in $subrepos) { $block += "/$s/" }
  }
  $block += $end

  $existing = @()
  if (Test-Path $giPath) { $existing = Get-Content $giPath }
  # strip any previous managed block, keep everything the user added outside it
  $out = New-Object System.Collections.Generic.List[string]
  $inBlock = $false
  foreach ($line in $existing) {
    if ($line -eq $beg) { $inBlock = $true; continue }
    if ($line -eq $end) { $inBlock = $false; continue }
    if (-not $inBlock) { $out.Add($line) }
  }
  while ($out.Count -gt 0 -and $out[$out.Count - 1].Trim() -eq "") { $out.RemoveAt($out.Count - 1) }
  if ($out.Count -gt 0) { $out.Add("") }
  foreach ($b in $block) { $out.Add($b) }
  Set-Content -Path $giPath -Value $out -Encoding utf8
}

function Sync-SubrepoMeta($unit, $subRepos) {
  # A DevOps sub-repo's internal metadata (CLAUDE.md, CONTEXT.md, CONTEXT_*.md, INBOX.md) is
  # excluded from the DevOps remote (Ensure-Excludes) AND cannot be tracked by the unit repo
  # directly (git refuses paths inside a nested repo). Backup: HARD-LINK each metadata file
  # into <unit>\.project-meta\<rel>\ - a tracked shadow path mirroring the repo's unit-relative
  # path. Same bytes, no sync step; the file in the project folder is the source of truth.
  # Self-heal: if an atomic save broke the link (hashes differ), relink from the project file.
  # (Same trick as settings.json above.) Role-level repos under the storage standard normally
  # carry no metadata (it lives in the project folder, directly tracked) - this then no-ops.
  foreach ($r in $subRepos) {
    $full = $r.Dir.FullName
    $relWin = $r.Rel -replace "/", "\"
    $names = @("CLAUDE.md", "CONTEXT.md", "INBOX.md") + `
      (Get-ChildItem $full -File -Filter "CONTEXT_*.md" | ForEach-Object { $_.Name })
    $metaFiles = $names | Where-Object { Test-Path (Join-Path $full $_) } | Select-Object -Unique
    if ($metaFiles.Count -eq 0) { continue }
    $shadowDir = Join-Path $unit (".project-meta\" + $relWin)
    if (-not (Test-Path $shadowDir)) { New-Item -ItemType Directory -Force -Path $shadowDir | Out-Null }
    foreach ($n in $metaFiles) {
      $srcFile = Join-Path $full $n
      $shadow = Join-Path $shadowDir $n
      if (Test-Path $shadow) {
        if ((Get-FileHash $shadow).Hash -eq (Get-FileHash $srcFile).Hash) { continue }
        Remove-Item $shadow -Force
      }
      New-Item -ItemType HardLink -Path $shadow -Target $srcFile | Out-Null
      Write-Host "     meta linked: .project-meta\$relWin\$n"
    }
  }
}

function Heal-Unit($unit) {
  $name = Split-Path $unit -Leaf
  Write-Host "== $name  ($unit)"
  if (-not (Test-Path (Join-Path $unit ".git"))) { git -C $unit init -q; Write-Host "   git init" }

  # safety: a unit repo must back up to an INTERNAL remote, never a customer's
  if ((Get-RemoteClass $unit) -eq "customer") {
    Write-Host "   WARNING: this unit repo has a NON-internal remote - internal notes could reach a customer."
    Write-Host "            point it at an internal remote (see ops/config/internal-remotes.txt)."
  }

  # NB: PS variable names are case-insensitive - keep these two names distinct
  $nestedRepos = Get-SubRepos $unit
  $nestedRels = @($nestedRepos | ForEach-Object { $_.Rel })

  Set-ManagedIgnore $unit $nestedRels
  if (Link-Harness $unit) { Write-Host "   harness linked" }
  Write-Host "   sub-repos ignored: [$($nestedRels -join ', ')]"

  foreach ($r in $nestedRepos) {
    $sp = $r.Dir.FullName
    Link-Harness $sp | Out-Null
    switch (Get-RemoteClass $sp) {
      "customer" { Ensure-Excludes $sp; Write-Host "     $($r.Rel): customer-facing -> ignored + guarded" }
      "internal" { Ensure-Excludes $sp; Write-Host "     $($r.Rel): internal remote -> ignored + guarded (wiki/shared: internal metadata still excluded)" }
      "none"     { Write-Host "     $($r.Rel): WARN no remote -> fold into the unit repo or add a remote" }
    }
  }
  Sync-SubrepoMeta $unit $nestedRepos

  $head = git -C $unit rev-parse --verify --quiet HEAD 2>$null
  if (-not $head) {
    # no 2>$null here: under EAP=Stop a redirected native stderr line (e.g. the LF/CRLF
    # warning on a fresh unit) becomes a terminating NativeCommandError; unredirected it is
    # just console output. (Same PS 5.1 trap as the two fixed 2026-07-06.)
    git -C $unit add -A
    git -C $unit commit -q --allow-empty -m "Initialize $name repo (local backup unit; DevOps sub-repos ignored)"
    Write-Host "   initial commit created"
  }
}

if ($Only) {
  Heal-Unit ((Resolve-Path $Only).Path)
} else {
  $units = @()
  $custRoot = Join-Path $Dev "customers"
  if (Test-Path $custRoot) { $units += (Get-ChildItem $custRoot -Directory | ForEach-Object { $_.FullName }) }
  $ownRoot = Join-Path $Dev "own"
  if (Test-Path $ownRoot) { $units += $ownRoot }
  foreach ($u in $units) { Heal-Unit $u }
}
Write-Host "done."
