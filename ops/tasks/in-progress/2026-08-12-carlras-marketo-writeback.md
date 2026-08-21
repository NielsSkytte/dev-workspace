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
- **The curated blocker cleared and the view rebuilt on deployed SQL** — `EmployeesIntervalSorting`
  restored and the CVR columns typed ([GEN-006] `734f9d5`, [GEN-007] `7944b67`), so the whole
  cascade builds. Full cause and evidence: `design/ATOMIC_GENERATOR_CHANGES.md`.
- **`outbound.Marketo_Lead` re-sourced from enriched, all-time** (`2ea82a8`). It read the curated
  star, which is windowed to three years and keyed order id through `dim.SalesOrder` — so 14.55% of
  invoice lines resolved to the orphan order and 10,824 leads were written a factual `0` beside real
  revenue. Now 218,350 rows, **zero false zeros**, and 75,413 leads regained the pre-window history
  the star could not see.
- **Contact grain scored against the write audit** (`marketo_fieldpush_reference`, not
  `enriched.Leads`, which carries account fields only): counts 66-86% exact where both sides hold a
  number, dates 70-85%. The largest block of apparent disagreement — 9,211 leads — is the incumbent
  writing `0` where we decline to, which is the defect we exist to fix.
- **The write path measured live** (other session, 2026-08-20): a null on a numeric or boolean
  Marketo field coerces to `0`/`false`, so "emit NULL, never a coalesced 0" is unimplementable and
  becomes three states with omission; and five of six date columns are `datetime`, which render a
  day early. [GEN-010] `f66e52f`, `tools/marketo_payload.py`, memory
  `marketo-write-precision-and-offset`.

## Next

> Two streams run in parallel and meet at `outbound.Marketo_Lead` and at the baseline.
> **Inbound** = landing zone -> raw -> enriched, which is what makes a baseline possible.
> **Outbound** = payload semantics and the push. Keep this list as the single queue for both.

**Inbound — blocked, fix ready and unproven**

1. **Prove the raw dedupe fix in DEV.** `PL_Ingest_Lakehouse_Raw_Marketo` fails with
   `DELTA_MULTIPLE_SOURCE_ROW_MATCHING_TARGET_ROW_IN_MERGE`: the extract re-reads the open month,
   so the pending batch carries several snapshots of the same lead and a Delta MERGE will not
   choose between them. It never failed before because 2026-08-10 was the table's first load, and
   a first load creates rather than merges. Fixed by an optional `prep_dedupeByKeyOrderBy` on
   `NB_Ingest_IngestChangedRecords`, set to `_lz_ingested_at_utc` for Marketo (`a106aec`); AX09
   and CVR pass nothing and are untouched. DEV's workspace is synced and correct — it just needs
   a run. Expect ~33,315 leads at one row per id, currency moving from 2026-08-10 to 2026-08-20.
2. **Then `PL_Transform_Enriched_Marketo`** to bring enriched forward; it is at 2026-08-10 too.
3. **Deploy the fix to TEST.** TEST runs the pre-fix definition and reads the same shared landing
   zone, so it fails the identical merge — three consecutive `PL_MainExecution` failures (08-19,
   08-20, 08-21 04:30 scheduled), and since `b721df8` the Marketo stage takes the whole run down.
   It will fail every morning until `NB_Ingest_IngestChangedRecords` and
   `PL_Ingest_Lakehouse_Raw_Marketo` are deployed.
4. **Then schedule the Marketo ingest daily.** This is the baseline: every Impact write becomes an
   SCD2 version, and "what we would push versus what is already there" becomes a query instead of
   archaeology. Blocked until 1-3, or the schedule just records corrupted history.

**Outbound**

5. **Build the push** — `PL_Outbound_Marketo` / `NB_Outbound_Marketo` on Marketo Bulk Import Lead
   (`importLead`), the endpoint Census uses. `tools/marketo_payload.py` already implements the
   three-state omission policy and the `-05:00` offset, so the notebook consumes that rather than
   re-deriving it.
6. **Build the comparison objects** — `outbound.Marketo_Lead_Delta` (one row per lead per field:
   our value, Marketo's value, verdict) plus a per-field summary. This is the artefact Niels asked
   for: it answers "what changes when we take over" without anyone reading SQL, and it is what
   says when we are ready to ask Impact to stop writing. Needs 1-4 first.

**Cross-cutting**

7. **Send the Impact mail** — the questions below. Longest turnaround of anything here and blocked
   by nothing.
8. **Surface the pushed fields in enriched.** `marketo_columns.include_in_enriched` flags 12 of the
   234 lead columns, which is why contact grain had to be scored from the write audit rather than
   `enriched.Leads`. Metadata change; the view generation is already metadata-driven.
9. **Re-score account grain** once inbound is current — the figures in
   `design/MARKETO_WRITEBACK_GOAL.md` (64.1% order count, 62.9% revenue) describe the old
   curated-sourced view and are stale.

## Open

*(Two items were resolved and removed 2026-08-21: `EmployeesIntervalSorting`, which shipped as
[GEN-006]/[GEN-007] and is written up in `design/ATOMIC_GENERATOR_CHANGES.md`; and the outbound
schemas being untracked locally, which `5642f32` settled.)*

- **Raise with Impact:** the incumbent zeroes ~1,650 Marketo leads a day via `coalesce(...,0)`.
- Missing inputs, both still unsupplied: `lookup_tables.cr_segment` (blocks the five segment flags
  and `Top20PctRevenue`) and `inriver_productdata` (blocks brand fields).
- Census sync behaviour (Update Only / Update or Create / Mirror) and null handling — the field
  mapping itself is already recovered from the audit trail.
- Reproduce or fix the account-grain store-count defect (distinct dates instead of order ids).
- **Two deliberate divergences from the incumbent that need to be stated decisions, not side
  effects.** Both come from sourcing the grain off the invoice line rather than the order header:
  3,402 leads gain a contact store count where Impact writes `0`, because we can classify
  header-less lines via the line's own `Dimension1` (99.94% coverage) and they cannot; and 898
  leads carry a positive Impact count where we produce nothing, not explained by window ageing —
  of 717 NULL latest-dates, only 5 have an Impact date older than 365 days.
- **`purchase_c` / `orderline_c` stay ingested through the transition** (Niels, 2026-08-21). They
  are AX09 data round-tripped into Marketo — `createdAt == updatedAt` on 100% of both — so they
  are the record of what Impact is actually writing, which is exactly what a takeover window
  needs. Turn them off entirely once the cutover is done. Note this contradicts the 2026-08-12
  "do not ingest" policy, deliberately and temporarily.
- **Marketo credentials are hardcoded in `NB_Ingest_Marketo`** (Niels, 2026-08-20) because a value
  typed onto a workspace notebook does not survive a git update and so cannot support a schedule.
  Temporary development credentials; **they must be cycled at the end of development** — they are
  in the repo's history now, so removing the line later is not the remediation.
- **PROD has no Marketo items at all** — not the lakehouse, not the warehouse, not the pipelines.
  Nothing has ever been deployed there, and extraction exists only in `Landingzone-Code-DEV`.

## Open with Impact — the questions and the mail that carries them

*(merged 2026-08-17 from `2026-08-10-carlras-marketo-fieldpush-owner` and
`2026-07-07-carlras-impact-marketo-mail`. Kasper (Impact) is the contact; Simon internally may know
which side owns the order feed. Deliverable is one `.md` file per `email-outlook-ready`, Danish per
`writing-voice`.)*

**Answered — do not re-ask.** The chain is established end to end:
`AX09 → Impact's Databricks silver_* → gold_census_contacts → Census → Marketo (importLead,
ben+carlras@impact.dk, ~07:10 UTC daily)`.

1. **Which account writes?** `ben+carlras@impact.dk` — Impact's, 99.8% of API-sourced changes.
2. **How often?** Daily, 2-3 bulk `importLead` batches inside 07:08-07:14 UTC, ~2,948 leads × 25
   fields each.
3. **What tool?** Census, now shipping as "Fivetran Activations" (Fivetran acquired Census
   2025-05-01).
4. **What is the transformation?** We hold it — four Databricks DLT files in `datahub/data/`,
   delivered 2026-06-22 with the GTM access and never described. `design/MARKETO_WRITEBACK_GOAL.md`
   sections 3-4.
5. **Store vs Online?** Three different rules: `WebOrderId != '0'` at account grain,
   `len(WebOrderId) > 2` for contact dates, and a 28-value `departmentId` whitelist for contact
   store counts.
6. **`Account Segment1` / `Account Discount Group`?** Master data from `silver_customer`:
   `CUSTTABLE.SEGMENTID` (100.0% agreement) and `CUSTTABLE.LINEDISC` (100.0%).
7. **`silver_*` → AX09 mapping** — derived from data 2026-08-12, no Impact involvement. Goal doc
   section 9.

**Still open — this is what the mail must ask.**

1. **Is the June SQL snapshot still current?** Files are from 2026-06-22. Partly self-checking (a
   ported rule that reproduces June but not August indicates drift, goal doc 4.6), but a direct
   confirmation is cheaper.
2. **The Census sync itself** — field-name mapping (`LatestOrderDateAccount` → `Latest Purchase
   Date Account`), schedule, matching identifier, and **sync behaviour** (Update Only / Update or
   Create / Mirror). That last one answers full-vs-delta push, which Marketo cannot tell us because
   it logs no no-ops. Ask for screenshots of the sync's mapping page and schedule — Census is
   dashboard-configured, there is no config file.
3. **How do they handle the date offset?** Measured live 2026-08-20: a bare date written to a
   Marketo `datetime` field is taken as UTC midnight and the instance renders UTC-5, so it
   **displays a day early** in the UI, the activity log, and every smart-list date filter. Five of
   our six date columns are `datetime`. Impact's own values carry the 18:00/19:00 time component on
   100% of records, so they send UTC midnight too — meaning Carl Ras has been segmenting a day
   early all along. Ask whether that is known and deliberate before we fix it: fixing it makes our
   values differ from theirs by a day during any parallel run. Detail: memory record
   `marketo-write-precision-and-offset`.
4. **Mapping residue:** `Status = 'Delivered'` is **not** `SALESSTATUS = 2` (that value covers 0.23%
   of orders while an unfiltered sum reproduces Marketo exactly) — settle before the port ships;
   `silver_address` has no ingested source (only feeds the Randers segment zip test); ~1/3 of
   accounts don't reproduce exactly despite median ratio 1.0000, with a cluster showing matching
   revenue at ~6× the order count, unexplained (suspect incumbent staleness); **AX09 history
   coverage** — `SALESTABLE` is effectively 2024+ in our landing zone while the invoice tables reach
   2016/2021: is upstream AX09 deeper, or is the extract windowed?
4. **Who writes the custom objects** (`purchase_c`, `orderLine_c`)? Their activities carry no
   `Modifying User`. Their write pattern spreads across the working day rather than batching, which
   points at the webshop or middleware rather than Impact's warehouse — **if so it is out of scope
   for the takeover.**
5. **Are we replacing the incumbent or running alongside first, and who agrees the cutover date?**
6. **`lookup_tables.cr_segment` and `inriver_productdata`** are referenced but not supplied. Only
   `cr_segment` matters (segment flags + `Top20PctRevenue`); `inriver_productdata` feeds brand
   fields that never reach Marketo.
7. **Nine defects need a reproduce-or-fix decision** (goal doc section 7). Three are real bugs:
   store order count counts distinct dates instead of order ids; account-grain counts and dates
   ignore the `Status = 'Delivered'` filter that the sums apply; email dedupe is nondeterministic.
   Raising these is also a courtesy — they are live defects in a system Impact still owns.
8. **Continued setup for Marketo API access** (the original 2026-07-07 mail item, cc Kasper) —
   fold into the same mail if still outstanding; the ingest side now runs, so verify before asking.

**Why it still matters:** retiring Databricks stops those Marketo fields updating. Nothing errors —
segmentation just starts targeting stale numbers.

## Log
- 2026-08-12 — workstream began (write-back reverse engineering, after the ingest chain was proven)
- 2026-08-14 — formalised as its own task; session time re-attributed here from
  `2026-07-07-carlras-impact-marketo-mail`, which is about API access, not the build
- 2026-08-16 — Next #1 attempted and blocked. Update-from-git in DEV first failed on a mangled
  `-- Auto Generated` header in `SalesLineTransactions.sql` that a workspace commit had corrupted
  (fixed and pushed, `0bc4977`); the Curated run then failed on `EmployeesIntervalSorting`.
  `outbound.Marketo_Lead` has still never been built in DEV.
- 2026-08-20 — blocker cleared: `EmployeesIntervalSorting` landed in Enriched CVR ([GEN-006]) and
  `outbound.Marketo_Lead` is built in DEV (218,350 rows). Task un-blocked; remaining work is the
  re-score, the push mechanism, and the Impact mail.
- 2026-08-20/21 — ingest blocked and the fix built. `PL_Ingest_Lakehouse_Raw_Marketo` fails the
  Delta MERGE on multiple source rows per lead; cause is the open-month re-read plus a stale
  `createdAt` export regime in the landing zone, and it only surfaced now because 2026-08-10 was
  the table's first load. Landing-zone ingest also could not run unattended: three parameters had
  no defaults so a scheduled trigger passed nulls, and the credentials were not in the workspace
  (`Landingzone-ETL` `d706f41`). Loader fix in `a106aec`. Two self-inflicted detours worth not
  repeating: pushing item definitions with `updateDefinition` broke the DEV pipeline because that
  API skips the logicalId/workspaceId translation the git import performs (repaired by Niels's
  sync), and a push carried an unrelated unpushed commit with it. **Standing rule from this:
  Claude does not run Update from git — Niels syncs the service.** Recorded in
  `datahub/CLAUDE.md`.
- 2026-08-21 — task file reconciled across the two parallel sessions (inbound and outbound) into a
  single Next queue; two resolved Open items retired.
- 2026-08-17 — MERGED: `2026-08-10-carlras-marketo-fieldpush-owner` (its eight open items were the
  same list as this task's Open section) and `2026-07-07-carlras-impact-marketo-mail` (the mail is
  the delivery vehicle for those questions). Note the 08-14 entry above: the mail task was about
  API access rather than the build — that item survives as question 8 and should be checked against
  the now-running ingest before it is asked.
