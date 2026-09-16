<#
  claude-accounts.ps1 - second Claude Code account on this machine.

  Claude Code keeps auth, config and session state in one directory, chosen by the
  CLAUDE_CONFIG_DIR environment variable (default %USERPROFILE%\.claude). One directory
  holds one logged-in account, so a second account needs a second directory.

  Verified on Claude Code 2.1.273 (2026-09-16): with CLAUDE_CONFIG_DIR set, .claude.json,
  .credentials.json, projects/ and history.jsonl are all created INSIDE that directory -
  the isolation is complete. (Older write-ups claim .claude.json stays global on Windows;
  that is no longer true.)

  Layout: %USERPROFILE%\.claude      = enterprise (Pingala AS) - the default, unchanged
          %USERPROFILE%\.claude-priv = private account - created here

  Shared, so the harness behaves the same on both accounts:
    settings.json, settings.local.json, CLAUDE.md   copied   (Claude Code rewrites these
                                                              in place, so a hard link
                                                              would silently break; re-run
                                                              this script to re-sync)
    commands\, skills\, tools\, plugins\            junction (one source of truth)

  NOT shared, on purpose: .credentials.json, .claude.json, projects\, history.jsonl,
  sessions\, file-history\, shell-snapshots\, caches.

  The workspace harness (C:\Dev\.claude - agents, hooks, commands, skills) is cwd-scoped,
  not account-scoped, so it is unaffected by the switch. Same for ops\memory, ops\time,
  ops\tasks: they are files under C:\Dev and both accounts write to them.

  Run:  powershell -NoProfile -File C:\Dev\ops\bin\claude-accounts.ps1
  Idempotent - safe to re-run; use it to re-sync after changing settings on the main side.
#>
param(
  [string]$AltName = ".claude-priv"
)

$ErrorActionPreference = "Stop"
$Main = Join-Path $env:USERPROFILE ".claude"
$Alt  = Join-Path $env:USERPROFILE $AltName
$Bin  = Join-Path $env:USERPROFILE ".local\bin"

if (-not (Test-Path $Main)) { throw "main config dir not found: $Main" }
if (-not (Test-Path $Alt)) {
  New-Item -ItemType Directory -Path $Alt | Out-Null
  Write-Host "created $Alt"
}

# --- shared files: copy (see header for why not hard links) ---
foreach ($f in @("settings.json","settings.local.json","CLAUDE.md")) {
  $src = Join-Path $Main $f
  $dst = Join-Path $Alt  $f
  if (-not (Test-Path $src)) { continue }
  $same = (Test-Path $dst) -and ((Get-FileHash $src).Hash -eq (Get-FileHash $dst).Hash)
  if (-not $same) { Copy-Item $src $dst -Force; Write-Host "synced  $f" }
}

# --- shared dirs: junction ---
foreach ($d in @("commands","skills","tools","plugins")) {
  $src = Join-Path $Main $d
  $dst = Join-Path $Alt  $d
  if (-not (Test-Path $src)) { continue }
  if (Test-Path $dst) { continue }
  cmd /c mklink /J "$dst" "$src" | Out-Null
  Write-Host "linked  $d"
}

# --- launchers on PATH (~\.local\bin is already ahead of everything) ---
if (-not (Test-Path $Bin)) { New-Item -ItemType Directory -Path $Bin | Out-Null }
$exe = Join-Path $Bin "claude.exe"
if (-not (Test-Path $exe)) { $exe = "claude" }

$cmdShim = @(
  '@echo off',
  ('set "CLAUDE_CONFIG_DIR=%USERPROFILE%\' + $AltName + '"'),
  ('"' + $exe + '" %*')
) -join "`r`n"
[IO.File]::WriteAllText((Join-Path $Bin "claude-priv.cmd"), $cmdShim + "`r`n", [Text.Encoding]::ASCII)

$shShim = @(
  '#!/bin/sh',
  ('CLAUDE_CONFIG_DIR="$USERPROFILE\' + $AltName + '" exec "' + $exe.Replace([char]92,[char]47) + '" "$@"')
) -join "`n"
[IO.File]::WriteAllText((Join-Path $Bin "claude-priv"), $shShim + "`n", [Text.Encoding]::ASCII)
Write-Host "shims   claude-priv(.cmd) -> $Alt"

Write-Host ""
Write-Host "Next: run 'claude-priv' in a NEW terminal, then /login with the private account."
Write-Host "Check which account a session is on with /status."
