# fab-as.ps1 - run the Fabric CLI (fab) as a named customer identity.
#
# Each customer gets its own fab config + token cache, so switching customers
# is instant and does not mean logging in again.
#
# Usage:
#   ops\bin\fab-as.ps1                   list customers, tenant, and login state
#   ops\bin\fab-as.ps1 Carl-Ras login    interactive login into that customer's tenant
#   ops\bin\fab-as.ps1 Carl-Ras ls       any fab command, run as that identity
#   ops\bin\fab-as.ps1 Carl-Ras          short for 'auth status'
#
# Mechanism: fab hard-codes its state to ~/.config/fab (see
# fabric_cli/core/fab_state_config.py, config_location()). It has no profile
# flag, so this script points USERPROFILE at a per-customer home for the child
# fab process only. Verified 2026-08-04: with USERPROFILE redirected, fab
# reports "Not logged in" while the original profile stays untouched.
#
# Homes live under %LOCALAPPDATA%\fab-profiles - a token cache must never sit
# in a git repo (AGENTS.md > Conventions > Secrets).
#
# Identity is read from the customer node's CLAUDE.md (tenant_id: / account:).
# One source of truth, no second registry to drift (Guardrail 11).

# Deliberately NOT an advanced function: no [CmdletBinding()], no declared
# arg array. Both would make PowerShell parse fab's own switches - '-o' binds
# to -OutVariable/-OutBuffer and errors as ambiguous. Plain $args passes every
# remaining token through untouched.
param([string]$Customer)

$FabArgs = @($args)

$ErrorActionPreference = 'Stop'

$WorkspaceRoot = Split-Path (Split-Path $PSScriptRoot)   # ops\bin -> ops -> C:\Dev
$CustomersRoot = Join-Path $WorkspaceRoot 'customers'
$HomesRoot     = Join-Path $env:LOCALAPPDATA 'fab-profiles'

function Get-CustomerIdentity {
    param([string]$Name)

    $node = Join-Path $CustomersRoot "$Name\CLAUDE.md"
    if (-not (Test-Path $node)) { return $null }

    $tenant  = ''
    $account = ''
    foreach ($line in Get-Content $node) {
        if (-not $tenant  -and $line -match '^tenant_id:\s*([0-9a-fA-F-]{36})') { $tenant  = $Matches[1] }
        if (-not $account -and $line -match '^account:\s*(\S+@\S+)')            { $account = $Matches[1] }
    }

    [pscustomobject]@{
        Name     = $Name
        Tenant   = $tenant
        Account  = $account
        Home     = Join-Path $HomesRoot $Name
        LoggedIn = Test-Path (Join-Path $HomesRoot "$Name\.config\fab\cache.bin")
    }
}

if (-not $Customer) {
    Get-ChildItem $CustomersRoot -Directory |
        ForEach-Object { Get-CustomerIdentity $_.Name } |
        Where-Object { $_ } |
        Select-Object Name,
            @{n = 'Cached';  e = { if ($_.LoggedIn) { 'yes' } else { 'no' } } },
            @{n = 'Account'; e = { if ($_.Account) { $_.Account } else { '(not set)' } } },
            @{n = 'Tenant';  e = { if ($_.Tenant) { $_.Tenant } else { '(not set)' } } } |
        Format-Table -AutoSize -Wrap
    Write-Host "Log in with: ops\bin\fab-as.ps1 <Customer> login"
    exit 0
}

$id = Get-CustomerIdentity $Customer
if (-not $id) {
    Write-Error "No customer node at $CustomersRoot\$Customer\CLAUDE.md. Run without arguments to list customers."
    exit 1
}
if (-not $id.Tenant) {
    Write-Error "Customer node $CustomersRoot\$Customer\CLAUDE.md has no tenant_id. Fill it in first (Guardrail 11)."
    exit 1
}

New-Item -ItemType Directory -Force -Path $id.Home | Out-Null
$env:USERPROFILE = $id.Home

if (-not $FabArgs -or $FabArgs.Count -eq 0) {
    $FabArgs = @('auth', 'status')
}
elseif ($FabArgs[0] -eq 'login') {
    $rest = @()
    if ($FabArgs.Count -gt 1) { $rest = $FabArgs[1..($FabArgs.Count - 1)] }
    $FabArgs = @('auth', 'login', '-t', $id.Tenant) + $rest
    if ($id.Account) { Write-Host "Sign in as $($id.Account) (tenant $($id.Tenant))." }
}

& fab @FabArgs
exit $LASTEXITCODE
