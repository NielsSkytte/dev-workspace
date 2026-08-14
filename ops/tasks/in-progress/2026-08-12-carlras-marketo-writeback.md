---
title: Carl Ras — Marketo write-back (outbound.Marketo_Lead, replacing Impact's Census sync)
status: in-progress
created: 2026-08-12
project: customers/Carl-Ras/datahub
owner: fabric-back
priority: high
blocked_by:
activity: MarketoImport
fno_task:
source: session
---

## What
Replace Impact's Databricks → Census → Marketo field push with a Pingala-owned outbound layer in
Fabric. Impact's `gold_census_contacts` is the table Census syncs; `outbound.Marketo_Lead` replaces
it.

Full derivation, validation and every source-column decision:
`customers/Carl-Ras/datahub/design/MARKETO_WRITEBACK_GOAL.md` (sections 9-14).

## Done
- **Source mapping derived from data alone**, no Impact involvement — `silver_order` =
  `CUSTINVOICEJOUR` + `CUSTINVOICETRANS`, `silver_customer` = `CUSTTABLE`, `silver_contact` =
  `CONTACTPERSON`, `departmentId` = `DIMENSION`. Scored against the Marketo `leads` table as an
  oracle.
- **Transformation rules settled** — `Status = 'Delivered'` means delivered *or* invoiced (so no
  status filter at all off the invoice tables); the 365-day contact window confirmed by a sharp
  peak; store/online splits differ by grain; `HasWebLogin` comes from `CONTACTPERSON.WEBLOGIN`,
  dropping the Microsoft Graph dependency.
- **`outbound.Marketo_Lead` built and pushed** (`Fabric-ETL` `5642f32`) — first reverse-ETL layer
  in this platform, on the existing curated star schema. No new ingest, no bespoke AX09 logic.
- **Order-to-contact link added to Atomic** so contact-grain measures are computable.

## Next
1. Update from git in Fabric-ETL-DEV → run `PL_Transform_Enriched_AX09` → run
   `PL_Transform_Curated` → re-score. Contact-grain has only been validated on a cached extract.
2. Build the push mechanism: `PL_Outbound_Marketo` / `NB_Outbound_Marketo` calling Marketo Bulk
   Import Lead (`importLead`) — the endpoint Census uses.
3. Move the Atomic contact-link extension into the generator (owner: Simon) — every regeneration
   drops it until then.

## Open
- **Raise with Impact:** the incumbent zeroes ~1,650 Marketo leads a day via `coalesce(...,0)`.
- Missing inputs, both still unsupplied: `lookup_tables.cr_segment` (blocks the five segment flags
  and `Top20PctRevenue`) and `inriver_productdata` (blocks brand fields).
- Census sync behaviour (Update Only / Update or Create / Mirror) and null handling — the field
  mapping itself is already recovered from the audit trail.
- Reproduce or fix the account-grain store-count defect (distinct dates instead of order ids).

## Log
- 2026-08-12 — workstream began (write-back reverse engineering, after the ingest chain was proven)
- 2026-08-14 — formalised as its own task; session time re-attributed here from
  `2026-07-07-carlras-impact-marketo-mail`, which is about API access, not the build
