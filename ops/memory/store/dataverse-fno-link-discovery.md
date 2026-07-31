---
id: dataverse-fno-link-discovery
ts: 2026-07-30T09:30:00Z
type: procedural
scope: workspace
source: session:746d591b
tags: [reference, dataverse, fno, d365, synapse, fabric, powerplatform, pac, tooling, matas]
description: "Name-independent discovery of which Dataverse environments are F&O-backed and whether their export link is real Azure Synapse or Link to Fabric; two PowerShell scripts at own/EnvDiscovery"
status: distilled
---

Two scripts under `own/EnvDiscovery/` (built in `customers/Matas/DataCompare/src/env-discovery/`,
moved out 2026-07-31 — the tooling is not Matas-specific). Built because we could not
assume environment **names** identify anything (a customer's "MFO"/"GFO" may be project names, not
environment names) and because the link *label* in the maker portal changed across product
versions ("Link to Synapse" -> "Azure Synapse Link" -> "data link"), so classification has to key
off stored markers.

## The four markers (all verified against a live tenant 2026-07-30)

| Question | Marker | Source |
|---|---|---|
| Is this environment F&O-backed? | `properties.finOpsMetadata.url` is set | Power Platform admin API |
| Is the export link a **real Azure Synapse** link? | a `datalakefolder` row with `isexternallake = 1` | Dataverse |
| Is it a **Link to Fabric**? | `synapselinkprofile.extendedproperties` contains `"LinkedToFabric":true` | Dataverse |
| Low-latency (delta) mode? | same profile also carries `"EnabledForDlw":true` | Dataverse |

Low-latency is **inference** from one correlated observation, not a documented contract.

## Scripts

- **`List-DataverseEnvironments.ps1`** — tenant-wide, needs Power Platform admin + the
  `Microsoft.PowerApps.Administration.PowerShell` module. No pac. Emits one row per environment
  incl. `DataverseUrl`, `IsFinOpsLink`, `FinOpsHost`, `FinOpsLinkType`, and the **specific** region
  (`properties.azureRegion` = e.g. `westeurope`, not the BAP geo `Location` = `europe`; plus
  `crmGeo`, `cluster.uriSuffix`, `cluster.geoShortName`).
- **`Get-EnvironmentDataLinks.ps1`** — per-environment, **pac CLI only, zero PowerShell modules**
  (an app registration was ruled out by the customer, so everything runs as the signed-in admin).
  Takes `-EnvironmentUrl`, `-EnvironmentName` (display names, may contain spaces), or
  `-EnvironmentCsv <List- output>`; `-FinOpsOnly` restricts to `IsFinOpsLink=True`. Runs on macOS.
  Needs a **Dataverse security role** per environment — Power Platform admin alone cannot read
  `synapselinkprofile`.

The two compose: `List-` produces the CSV that `Get-` consumes, carrying `DisplayName`,
`AzureRegion`, `IsFinOpsLink`, `FinOpsHost` into the link report.

## Things that looked right and were not

- **`properties.linkedAppMetadata`** — the obvious-looking F&O marker. Empty on known-F&O
  environments. The real one is `finOpsMetadata`.
- **`synapselinkprofile.profiletype`** — cannot distinguish Fabric; the option set is only
  `0=SynapseLink`, `1=EventAnalytics`. A known Fabric link reads `SynapseLink`.
- **`StorageAccountName`** on the profile — literally `"mock"` on every profile.
- **`datalakefolder.path`** — empty on the external-lake folder, so a `LIKE` filter on it silently
  matches nothing.
- **Counting Synapse links as `ActiveLinks - FabricLinks`** — overcounts (said 3, portal showed 1);
  internal/system profiles inflate it. Count external lakes instead.
- **Table counts must be scoped to the profile.** Counting all active
  `synapselinkprofileentity` rows reported 108 Dataverse tables for an environment the portal
  showed as 0-of-1004 selected — the rows sat on internal profiles.
- **F&O virtual-table counts (`mserp_` prefix) measure a different population** than the wizard's
  "available" number (252 vs 3640). Dropped, not reported. The "available" side is metadata/catalog
  and is not queryable from Dataverse at all — the scripts report only what is **selected**.
- **The Fabric workspace name is not in Dataverse.** `datalakeworkspace` is the ADLS concept;
  its rows are Dataverse workspaces. Getting the linked Fabric workspace needs the Fabric REST API.

## pac + Windows PowerShell 5.1 traps

- **`pac env fetch --xml "<fetch>...</fetch>"` is unusable from PowerShell 5.1** — inner double
  quotes reach the native command unescaped and pac fails with a non-recoverable error on every
  environment. Always write a temp file (UTF-8 **no BOM**) and pass `--xmlFile`.
- **`pac auth create --deviceCode` prints the code to stdout**, so `$x = Invoke-Pac ...` swallows
  it and the run looks hung. Pipe interactive pac calls through `| Out-Host` and return only
  `$LASTEXITCODE`.
- **`pac env fetch` has no `--json`** — it returns fixed-width text. Prefer FetchXML `aggregate`
  count queries and split result lines on `\s+` (not two-or-more spaces: `cnt ptype pstate`
  headers are single-spaced).
- **Some entities reject aggregates** ("FetchExpression cannot be converted because aggregates
  aren't supported by QueryExpression" on `datalakefolder`) — fetch the rows and count client-side.
- **Never parse localised labels.** Dataverse returns `Ja/Nej` on a Danish tenant; filter
  server-side on numeric values and, when scraping text output, key off lines containing a GUID
  rather than on header words.
- Return `[pscustomobject]@{ Rows = $rows }` from parse helpers — bare `,$rows` collapses so the
  caller cannot tell "unparseable" from "parsed, zero rows".

## Setup for a recipient admin (macOS)

`brew install --cask powershell` -> .NET 8 SDK ->
`dotnet tool install --global Microsoft.PowerApps.CLI.Tool` (pac lands in `~/.dotnet/tools`) ->
`pac auth create --name env-discovery --deviceCode`. The script also creates the profile itself
via `-Login`.
