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

# --- mods: every folder under C:\Dev\.claude\mods that holds a plugin.json is loaded in both accounts ---
$ModsRoot = "C:\Dev\.claude\mods"
$mods = @(Get-ChildItem $ModsRoot -Directory -ErrorAction SilentlyContinue |
  Where-Object { Test-Path (Join-Path $_.FullName ".claude-plugin\plugin.json") } |
  Sort-Object Name | ForEach-Object { $_.FullName })
# Orca's agent-view plugin (Orca terminal app). Orca passes it in its own CLAUDE_CODE_PLUGIN_DIRS,
# which the settings.json env replaces, so it is added here. The plugin does nothing outside Orca
# (no ORCA_AGENT_HOOK_TOKEN). The hash folder changes with Orca updates: re-run this script then.
$OrcaView = Join-Path $env:APPDATA "orca\claude-agent-view"
$mods += @(Get-ChildItem $OrcaView -Directory -ErrorAction SilentlyContinue |
  Sort-Object LastWriteTime -Descending | Select-Object -First 1 |
  ForEach-Object { Join-Path $_.FullName "orca-agent-view" } |
  Where-Object { Test-Path (Join-Path $_ ".claude-plugin\plugin.json") })
$mainSettings = Join-Path $Main "settings.json"
if ($mods.Count -gt 0 -and (Test-Path $mainSettings)) {
  $value = ($mods -join ";").Replace("\", "\\")
  $text = [IO.File]::ReadAllText($mainSettings)
  $new = [regex]::Replace($text, '("CLAUDE_CODE_PLUGIN_DIRS"\s*:\s*)"[^"]*"', { param($m) $m.Groups[1].Value + '"' + $value + '"' })
  if ($new -ne $text) { [IO.File]::WriteAllText($mainSettings, $new, (New-Object Text.UTF8Encoding($false))); Write-Host "mods   $($mods.Count) registered" }
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

# c-w = enterprise, c-p = private. Each launcher sets the account explicitly, so an inherited
# CLAUDE_CONFIG_DIR (e.g. a terminal app started from a private session) cannot pick the account.
# c-w UNSETS the variable rather than pointing it at ~\.claude: unset keeps .claude.json in
# %USERPROFILE%, where the enterprise login lives. The exe is called by full path, past any wrapper.
$shExe = $exe.Replace([char]92,[char]47)
$launchers = @(
  @{ Name = "c-w"; Cmd = 'set "CLAUDE_CONFIG_DIR="'; Sh = 'unset CLAUDE_CONFIG_DIR' },
  @{ Name = "c-p"; Cmd = ('set "CLAUDE_CONFIG_DIR=%USERPROFILE%\' + $AltName + '"'); Sh = ('export CLAUDE_CONFIG_DIR="$USERPROFILE\' + $AltName + '"') }
)
foreach ($l in $launchers) {
  $cmdShim = @('@echo off', 'setlocal', $l.Cmd, ('"' + $exe + '" %*')) -join "`r`n"
  [IO.File]::WriteAllText((Join-Path $Bin ($l.Name + ".cmd")), $cmdShim + "`r`n", [Text.Encoding]::ASCII)
  $shShim = @('#!/bin/sh', $l.Sh, ('exec "' + $shExe + '" "$@"')) -join "`n"
  [IO.File]::WriteAllText((Join-Path $Bin $l.Name), $shShim + "`n", [Text.Encoding]::ASCII)
}
# the old claude-priv launcher is replaced by c-p
foreach ($old in @("claude-priv", "claude-priv.cmd")) {
  $p = Join-Path $Bin $old
  if (Test-Path $p) { Remove-Item $p -Force; Write-Host "removed $old" }
}
Write-Host "shims   c-w(.cmd) -> enterprise ($Main), c-p(.cmd) -> private ($Alt)"

Write-Host ""
Write-Host "Next: open a NEW terminal; c-w starts enterprise, c-p starts private."
Write-Host "Check which account a session is on with /status."
