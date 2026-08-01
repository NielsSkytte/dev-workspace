---
id: fno-vendor-gab-link-scope
ts: 2026-08-01T12:42:00Z
type: procedural
scope: workspace
source: session:11777a94
tags: [d365, fno, dataverse, linktofabric, vendor, gab, dirparty, matas, extraction]
description: "The 13 F&O tables a vendor-master extract needs via Link to Fabric, why VendTable alone gives blank names, and which columns were verified present in a live tenant"
status: distilled
---

The F&O vendor master is **split between the AP layer and the Global Address Book**. A
`VendTable`-only Link-to-Fabric scope yields vendors with **no name and no address**. Ask for
all of these in Manage tables (the search box accepts a pasted comma-separated list):

```
DATAAREA, DirPartyLocation, DirPartyLocationRole, DirPartyTable, DirPersonName,
LogisticsAddressCountryRegion, LogisticsElectronicAddress, LogisticsElectronicAddressRole,
LogisticsLocation, LogisticsLocationRole, LogisticsPostalAddress, VendBankAccount, VendTable
```

## What each earns its place with

| Table | Fields |
|---|---|
| `VendTable` | AccountNum, VendGroup, PaymTermId, TaxGroup, Currency, VatNum, Blocked (7) |
| `DirPartyTable` | Name, NameAlias, LanguageId, InstanceRelationType + `PARTYNUMBER` (the global-party grain) |
| `DirPersonName` | person name parts (4) - NULL for organizations |
| `LogisticsPostalAddress` | Street, City, ZipCode, CountryRegionId, formatted address (5) |
| `LogisticsElectronicAddress` | phone, extension, email (3) |
| `LogisticsLocation` | address description |
| `LogisticsAddressCountryRegion` | ISO code |
| `Logistics*Role` + `DirPartyLocation*` | role/purpose lists |
| `VendBankAccount` | not a field source - a **cross-system match key** (bank/IBAN exists in AX and NAV too) |
| `DATAAREA` | kernel table, legal-entity list; no change tracking needed, 24h refresh |

## Verified in a live tenant (2026-07-31, Matas)

- `DirPartyTable` **does** carry `primaryaddresslocation`, `primarycontactphone`,
  `primarycontactemail` - so the address/contact joins go direct and do not need to route
  through `DirPartyLocation`. This was the assumption most likely to be wrong; it held.
- Table names land **lowercase**; `IsDelete` is mixed case. Resolve columns case-insensitively.
- Metadata tables arrive automatically: `GlobalOptionsetMetadata` (note the **set**),
  `OptionsetMetadata`, `StateMetadata`, `StatusMetadata`, `TargetMetadata`.
- `fab table schema <ws>/<lakehouse>.Lakehouse/Tables/<t>` verifies every required column
  **without running anything in Fabric** - do this before writing notebook code against a schema.

## Provenance rule worth keeping

A customer-supplied "field list" (here a Dynamics data-entity export sheet) names **fields**,
never tables. The table list is always ours to derive and ours to defend. Say so plainly when
asked what came from whom.

Also documented: Synapse Link **blocks staging/temp/`del_` tables**, and custom F&O tables
need change tracking enabled before they appear. See [[dataverse-fno-link-discovery]].
