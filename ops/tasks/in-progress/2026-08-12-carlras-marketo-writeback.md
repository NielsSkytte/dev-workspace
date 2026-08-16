---
title: Carl Ras — Marketo write-back (outbound.Marketo_Lead, replacing Impact's Census sync)
status: in-progress
created: 2026-08-12
project: customers/Carl-Ras/datahub
owner: fabric-back
priority: high
blocked_by: viewtransform.CentralCompanyRegister (Warehouse_Enriched_CVR) does not expose EmployeesIntervalSorting
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
1. **BLOCKED — unblock `EmployeesIntervalSorting` first, then resume.** Next #1 was attempted
   2026-08-16 and got as far as Curated. `viewdimtransform.Customer` reads
   `[CentralCompanyRegister].[EmployeesIntervalSorting]`, and nothing produces that column:
   `Warehouse_Enriched_CVR.enriched.CentralCompanyRegister` exposes `EmployeesYear`, `Employees`,
   `EmployeesFte`, `EmployeesInterval` and no sorting column, in the repo or live. The column
   appears **only** on the consumer side — `viewdimtransform/Views/Customer.sql` and
   `dim/Tables/Customer.sql`, both arrived by workspace commit (`1baffda`, `e7c9f51`). One
   missing column produced fourteen CTAS failures in one run:

   | sub-pipeline | error | object |
   |---|---|---|
   | `_Dim` | 207 invalid column `EmployeesIntervalSorting` | `viewdimtransform.Customer` |
   | `_Bridge` | 208 invalid object `dim.Customer` | `CustomerToContacts` |
   | `_Fact` | 208 invalid object `dim.Customer` | `SalesTransactions`, `SalesForecasts` |
   | `_Outbound` | 208 invalid object `fact.SalesTransactions` | **`viewoutboundtransform.Marketo_Lead`** |

   So `outbound.Marketo_Lead` cannot build until a CVR-side column lands. The fix is in the
   Enriched CVR producer, not in this workstream — see Open.
2. Then re-run: Update from git in Fabric-ETL-DEV → `PL_Transform_Enriched_AX09` →
   `PL_Transform_Curated` → re-score. Contact-grain has only been validated on a cached extract.
3. Build the push mechanism: `PL_Outbound_Marketo` / `NB_Outbound_Marketo` calling Marketo Bulk
   Import Lead (`importLead`) — the endpoint Census uses.
4. Move the Atomic contact-link extension into the generator (owner: Simon) — every regeneration
   drops it until then.

## Open
- **`EmployeesIntervalSorting` is not this task's to fix** — it belongs to the CVR enriched layer
  and the Customer dimension. Proposed mapping, ascending by size, `999` for no match (which is
  already what `viewdimtransform.Customer` falls back to on line 175):
  `ANTAL_0_0` 0, `ANTAL_1_1` 1, `ANTAL_2_4` 2, `ANTAL_5_9` 3, `ANTAL_10_19` 4, `ANTAL_20_49` 5,
  `ANTAL_50_99` 6, `ANTAL_100_199` 7, `ANTAL_200_499` 8, `ANTAL_500_999` 9,
  `ANTAL_1000_999999` 10, NULL/other 999. Row counts for each bucket are in the session log.
  Probably deserves its own task rather than living here.
- **`PL_Transform_Curated_Outbound` and the `outbound` / `outboundtransform` /
  `viewoutboundtransform` schemas exist in DEV but are untracked in the local clone** — they were
  authored in the workspace. Confirm they are committed before any TEST hop.
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
- 2026-08-16 — Next #1 attempted and blocked. Update-from-git in DEV first failed on a mangled
  `-- Auto Generated` header in `SalesLineTransactions.sql` that a workspace commit had corrupted
  (fixed and pushed, `0bc4977`); the Curated run then failed on `EmployeesIntervalSorting`.
  `outbound.Marketo_Lead` has still never been built in DEV.
