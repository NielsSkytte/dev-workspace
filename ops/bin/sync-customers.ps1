<#
  sync-customers.ps1 - push customer unit repos (C:\Dev\customers\<Customer>), with their git
  history, into one folder each of Niels's PRIVATE GitHub repo NielsSkytte/customers.
  Personal backup only: credentials (.secrets/) travel with it on purpose (AGENTS.md >
  Conventions, secrets rule). Never point it at atompower4us or any shared or customer remote.

  Run:  powershell -NoProfile -File C:\Dev\ops\bin\sync-customers.ps1 Carl-Ras [Matas ...]
        ... -NoPush     build locally, push nothing
  Only committed work travels. Wraps sync-aai.ps1 with its own work dir.
#>
[CmdletBinding(PositionalBinding = $false)]
param(
    [Parameter(ValueFromRemainingArguments = $true)] [string[]] $Customers,
    [switch] $NoPush
)
$ErrorActionPreference = 'Stop'
if (-not $Customers) { throw 'name one or more folders under C:\Dev\customers' }
$a = @{
    Remote = 'https://github.com/NielsSkytte/customers.git'
    Root   = 'C:\Dev\customers'
    Work   = (Join-Path $env:LOCALAPPDATA 'customers-sync')
}
if ($NoPush) { $a.NoPush = $true }
& (Join-Path $PSScriptRoot 'sync-aai.ps1') @a @Customers
