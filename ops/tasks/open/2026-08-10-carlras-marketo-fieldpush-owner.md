---
title: Carl Ras — identify who computes and pushes the AX09 aggregates into Marketo (Databricks migration blocker)
status: open
created: 2026-08-10
project: customers/Carl-Ras/datahub
owner: fabric-back
priority: high
blocked_by:
activity: MarketoImport
fno_task:
source: handoff
---

## What
Establish which system computes the commerce aggregates on Marketo person records
(`Total Sales Account`, `Order Count Contact`, `Latest Purchase Date Account Store`, …) and
pushes them into Marketo over the REST API — and on what schedule.

**Partly answered from the data on 2026-08-10** (see Evidence). Still open:
1. ~~Which account holds the Marketo API credentials?~~ **`ben+carlras@impact.dk`** — an Impact
   account, 99.8% of API-sourced field changes, via `importLead`.
2. ~~How often does it run?~~ **Daily at 07:00 UTC**, 69 of 69 observed days.
3. **Which system runs it?** Still unknown. The Marketo user is Impact's; whether the job runs in
   the Databricks Data Hub or elsewhere in Impact's estate is not established.
4. **Where does it read from** — Databricks, AX09 directly, or something else?
5. **Is the aggregation logic documented or readable anywhere?** Specifically: what marks a sale
   as `Store` vs `Online`, and how are `Account Segment1` and `Account Discount Group` derived?
6. Are we replacing it or running alongside it first, and who agrees the cutover date?

Kasper (Impact) is the contact. Simon internally may know which side owns it.

## Why
**This is a migration blocker, and it fails silently.**

Pingala replaces whatever is in Databricks. If the field-push job lives there, switching Databricks
off stops those Marketo fields updating. Nothing errors — Marketo campaign segmentation simply
starts targeting stale sales figures, and nobody finds out until someone notices a campaign
behaving oddly.

## Evidence
From the landed Marketo activity data, 2026-08-10 (`design/MARKETO_INGEST_DESIGN.md` §7):

- `Change Data Value` (activity type 13) is **44.7% of activity rows, 53.4% of payload** —
  3,099,313 rows across 54,920 people.
- 97 distinct changed fields; top 20 = 94.2%. Roughly **66% are commerce aggregates**:
  `Total Sales` / `Order Count` / `Latest Purchase Date`, at both `Account` and `Contact` grain,
  each split blank / `Store` / `Online`.
- The `source` attribute is **`Web service API` on 69.6%** of type-13 rows
  (`Marketo Flow Action` 30.2%, everything else 0.2%).

**Updated 2026-08-10 — both earlier inferences are now measured.**

- The `Modifying User` attribute names the caller directly: **`ben+carlras@impact.dk`**, on
  2,153,157 of 2,157,817 API-sourced rows (**99.8%**), via `API Method Name = importLead`.
  Impact operating the job is therefore **established**. *Which* Impact system runs it is not.
- `source` x field cross-tabulated: every commerce field is **100% `Web service API`**; both
  `Soft Bounce` fields are **100% `Marketo Flow Action`**. The two groups do not overlap.
- Cadence: **99.8% of push volume lands in the 07:00 UTC hour**, on 69 of 69 days.

Full derivation: `design/MARKETO_WRITEBACK_GOAL.md`. Reference data:
`Lakehouse_Util.marketo_fieldpush_reference` (3,099,313 rows).

## Why it matters beyond the block
The same field list is the **requirement spec for the Marketo write-back workstream** (Niels,
2026-08-10: *"we just need to replicate what they are aggregating from our version and push that to
Marketo"*). AX09 is already in Fabric — only the aggregation and the push are missing.

The type-13 change log additionally gives the **cadence** and the **value history** of the incumbent
job, so a Fabric replacement can be validated against what is actually being written today rather
than against a spec.

Recommend capturing and retaining **one clean type-13 window as the reference set** before type 13
is excluded from routine activity ingest (§7.5).

## Log
- 2026-08-10 — created (handoff from the Marketo activity-data exploration)
