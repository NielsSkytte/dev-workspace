---
title: Carl Ras — operation_hardening (keep PL_MainExecution running green across DEV/TEST/PROD)
status: in-progress
created: 2026-08-11
project: customers/Carl-Ras/datahub
owner: fabric-back
priority: normal
blocked_by:
activity:
fno_task: CarlRData-555
customer_ask: none
source: direct
---

## What
operation_hardening — make the daily `PL_MainExecution` chain run green and keep it that way.
Covers the run-failure work that follows the SPN-auth migration and the key-map/join fixes:
diagnosing and closing each remaining failure in the chain, and removing the classes of
fragility that produce them.

Open at creation (measured 2026-08-11):
- **TEST**: scheduled runs 08-10 and 08-11 fail at the last stage only — `Semantic Model` →
  `PL_Update_SemanticModel` → `Notebook1` (`NB_Refresh_SemanticModel`), `403 Forbidden` on the
  refresh POST. Raw/Enriched/Curated pass. TEST `Model` last refreshed 2026-08-07 06:54 UTC.
- **DEV**: no run since 2026-08-07 12:09 (Failed on `VL_ConnectionId|CON-SQLFabric-ETL_Lakehouse_Util`
  → `VariableNotFound`); that run predates commits `0d2dc5b` and `9153a8e`. Both DEV schedules disabled.
- **PROD**: no job instances; schedule disabled, owner is a user account.

### Current blocker — semantic model refresh fails on a Currency overflow

*(merged 2026-08-17 from `2026-08-14-carlras-semanticmodel-currency-overflow`; owner: semantic)*

`PL_MainExecution` in DEV now reaches its final stage and fails there. Run 2026-08-14
07:03:13 → 08:50:18 UTC (1h47m): **Raw, Enriched and Curated all passed**, `Semantic Model`
failed.

```
Operation on target Semantic Model failed:
  Operation on target Notebook1 failed:  (NB_Refresh_SemanticModel)
    refresh Failed:
      "Retry attempts for failures while executing the refresh exceeded the retry limit"
      0xC112001A  "Value was either too large or too small for a Currency.
                   The exception was raised by the IDataReader interface."
```

A value arriving from Curated is outside the range a Fixed Decimal / Currency column can
hold (±922,337,203,685,477.5807). The refresh retries, keeps hitting it, and gives up.

**This is a different failure from the 403.** `PL_Update_SemanticModel` last failed 2026-08-11 with
`403 Forbidden` on the refresh POST. That authorisation problem is not what happened here — the
refresh started and ran. Whether the 403 is also still latent is unknown; it did not surface this
time. It is also **not a regression**: this is the first refresh ever attempted against a
freshly-built Curated layer — `PL_Transform_Curated` had never completed before 2026-08-14.

**Where to look.** Sweep the money columns of the Curated facts for out-of-range values:

```sql
-- per candidate column, on Warehouse_Curated
SELECT MIN([col]), MAX([col]) FROM [fact].[SalesTransactions];
-- anything beyond ±922,337,203,685,477.5807 cannot land in a Currency column
```

**Lead, inference not diagnosis:** `viewtransform.SalesLineTransactions` and
`SalesInvoiceTransactions` both compute money through divisions guarded only by `NULLIF`, e.g.
`/ salesline.[Qty_Scaled]` and `/ COALESCE(NULLIF(exchrates.[EXCHRATE],0)/100,1)`. `NULLIF`
catches an exact zero but not a very small non-zero denominator, which would produce an
enormous quotient. Worth checking before assuming bad source data. Also worth ruling in or out:
whether the tables inflating their row counts
(`2026-08-14-carlras-enriched-rowcount-failures`) contribute — duplicated rows do not change an
individual value, so unlikely, but both findings sit in the same fact lineage.

**Blocked on: consult the semantic model developer first** (Niels's call, 2026-08-14). The fix may
belong in the model (column data type — Fixed Decimal vs Decimal) rather than in Curated, and that
is the model owner's decision. Do not change Curated column types unilaterally.

## Progress

**Now (2026-09-25):** DEV->TEST: `Warehouse_Curated` deployed 09-25 07:14 after its table files were matched to the CTAS views (`3d3c70d`, `f0ca063`); DEV refilled by `PL_Transform_Curated`, TEST tables full. `Warehouse_Enriched_AX09` failed to TEST 09-24 11:21, 09-25 08:40 and 09:44 (`SQL71561`/`SQL71508`): the deploy build cannot see `Lakehouse_Raw_AX09`'s columns. Fixed by GEN-014 (7 prefixes, `ed158d6`) + GEN-015 (4 Raw `*` -> named lists, `8ed2333`); deployed to TEST 09-25 15:05 UTC, succeeded. TEST's Curated/AX09/CVR/GTM views now equal git view-for-view (32/60/1/1). `tools/wh_rules.py` now runs in pre-push. The error class changed between 09-09 (import-time `Invalid object name`) and 09-14 (`SQL Project build failed` SQL715xx); inference: Fabric added a SQL-project build before import in that window.
**TEST->PROD (measured 09-25):** PROD last took a full deploy 09-09 10:33 (50 items ok; `Warehouse_Enriched_GTM`/`_Marketo` failed `Invalid object name` on the PROD raw tables, not loaded yet then). 09-14 Curated->PROD failed with the SQL71501 since fixed. PROD warehouses: Curated 0 tables, AX09 3, CVR 0, GTM/Marketo empty shells. Not yet checked (read blocked by auto mode): PROD raw tables `events`/`leads`/`activities`, PROD value sets, PROD workspace identity.

**Then (2026-09-23):** refresh starts at rung 2; `max_rung=2` kept; forcing rung 1 is a one-off notebook run with `start_at_rung=1`.

**Tried and dropped:** model ownership (`TakeOver`) as the cause of the refresh 403 -> disproved 08-11, the
cause is the Fabric-minted notebook token; sempy / semantic-link-labs in the refresh -> REST enhanced refresh
with a Key Vault-minted token; a fixed wait after the scale -> the scale inside `PL_MainExecution` (08-20); GEN-014 CTE aliasing `cit`/`sl` (reverted `c99c477`, not the fix); Raw SQL endpoint metadata refresh (all 90 tables `NotRun`, already in sync, 09-25); DacFx 2.3.0 as the trigger (same local results as 2.2.0).

**Next:**
1. Run the AX09 enriched transform in TEST and check row counts (deploy done 09-25 15:05). Measured 09-25: DEV=TEST for all 47 notebooks/pipelines/libraries (ids aside; only the schedule flag differs) and all warehouse views; TEST tables still from the 09-24 04:30 run (e.g. `outbound.Dataverse_Contact` 5000 = the old TOP). No TEST scheduled run on 09-25 although the Mon-Fri schedule is enabled; cause not established. `enriched.DeliveryAddress` is empty in DEV and TEST: table file in git, no view builds it.
1b. TEST->PROD done 09-25 (portal, Niels): all Fabric-ETL items incl. 5 warehouses (old GTM/Marketo shells deleted; Curated needed a second deploy - it imports before CVR creates `enriched.CentralCompanyRegister`, so deploy Enriched first, Curated second). TEST run 9b63f26c green 15:34-17:08 UTC. PROD seed ran (GetEnums fails: Pingala's own Key Vault/D365, no stage has an enums table), NB_Metadata_Marketo ran, identities re-stamped to the SPN. PROD `PL_MainExecution` schedule is ON (came with the deploy). Open: PROD connections `CON_Notebook_WI_PROD` + a WI SQL connection to PROD `Warehouse_Enriched_Marketo` (creation blocked for Claude by auto mode - Niels), then `VL_ConnectionId` Prod.json; `VL_DatastoreId` Prod.json fixed locally (CVR pointed at Curated's id), not committed.
2. Run `NB_Refresh_SemanticModel_Full` once with `start_at_rung=1`, `max_rung=2`, off-hours (Niels).
3. Verify the 06:30 run completes end to end (`CapacitySku = F32` rows in `Lakehouse_Util.SemanticModelRefreshLog`).
4. Re-stamp TEST's `PL_MainExecution` schedule to the SPN (`tools/fabric_release.py`).

## Needs from customer

- None.


## Why
The chain is the platform's daily heartbeat. Raw/Enriched/Curated are current but the TEST
semantic model has been stale since 2026-08-07, and PROD has never been exercised. Every failure
so far has been an identity, variable-library or key-map issue rather than data logic — the same
classes will keep recurring until they are closed deliberately.

## Context
- `customers/Carl-Ras/datahub/CONTEXT.md` — project state; the semantic-model refresh/memory work.
- `customers/Carl-Ras/datahub/CLAUDE.md` — the 2026-08-11 conventions: nothing per-environment
  hardcoded; variable libraries are the environment contract; `Lakehouse_Util` must be seeded.
- `Fabric-ETL/Orchestration/Schedule/PL_MainExecution.DataPipeline` → Raw / Enriched / Curated /
  Semantic Model; the last stage is `PL_Update_SemanticModel` → notebook logicalId
  `33e45f7b-5e2d-86e7-48fb-e834b0d9a6f2` (`NB_Refresh_SemanticModel`, the old per-table plan).
  `NB_Refresh_SemanticModel_Full` exists but the pipeline does not point at it.
- `tools/fabric_identity.py` — the SPN identity migration; it has no semantic-model takeover.
- Measured on the 403: the SPN (`aa462763…` / object `f05f446a…`, the TEST schedule owner) reads
  the dataset and its refresh history over the Power BI API (200), and the dataset's
  `configuredBy` is `EXT_NSKC@carl-ras.dk`. Model ownership as the cause is inference, untested.
- Related tasks: `2026-07-07-carlras-fabric-scaleup` (capacity/model processing),
  `2026-07-16-carlras-gtm-inbound-ingest` (GTM is not yet in `PL_Execute_Raw`).

## Log
- 2026-08-11 — created; started (session task)
- 2026-08-17 — MERGED: `2026-08-14-carlras-semanticmodel-currency-overflow` folded in as the
  current blocker — it is the last stage of this same chain and was created stating so.
  `blocked_by` now carries the semantic-model-developer consult.
- 2026-09-21 — check-in: TEST Key Vault identity added by Carl Ras; PROD SQL endpoints resolved. Progress rewritten. Needs from customer cleared.
- 2026-08-19 — UNBLOCKED: the Currency overflow is closed. Cause was one AX09 row
  (`crcampaignforecast.RecId` 5638443880, `ForecastQuantity` 2222222222222222, entered by `SOUR`
  2026-08-18 09:03), not a model or Curated defect. `Campaign Forecasts[Forecast Quantity]` retyped
  Fixed Decimal Number -> Decimal Number; TEST refresh green at 08:11 (14 min, five adaptive
  batches after one memory-ceiling probe at 5090/5084 MB). Fix is in `Semantic-Model` `503b5d4`
  and live in Semantic-Model-DEV, so a DEV->TEST deployment no longer reverts it. AX09 record
  correction initiated by Niels. Data-quality gate spun out as
  `2026-08-19-carlras-atomic-dataquality-gate`. Still open in this chain: the Marketo failure from
  the same run.
- 2026-08-27 — TEST's `PL_MainExecution` fails at `Scale Up` with `Failed to resolve connection ''`
  (`InvalidExternalReferenceConnection`), runs 08-23 15:12 and 08-24 04:30. Cause: `Test.json`
  overrides `VL_ConnectionId.CON-WI-Notebook` with an empty string on purpose (`356df51`); the scale
  moving into `PL_MainExecution` (`747d9f2`) plus the live TEST schedule (`fda1d4b`) made it fatal.
  Created `CON_Notebook_WI_TEST` (`c54d4c1b-980e-411c-ba38-dfb8db960604`, WorkspaceIdentity),
  granted `User` on it to the schedule SPN `f05f446a…`, and pointed `Test.json` at it in
  `Fabric-ETL` `ebee979` (pushed). **Not yet green — two steps outstanding, neither ours:**
  (1) Update from git in `Fabric-ETL-DEV` + deploy `VL_ConnectionId` to TEST — both workspaces still
  read `""` as of 08-27; (2) Carl Ras must add `85553fa2-1343-4d6e-89e4-433fd51ba6a6`
  (`Fabric-ETL-TEST` workspace identity, **object** id) to `Fabric_Key_Vault_Users` — they added DEV
  and PROD instead. Without (2) the run clears the connection error and fails in
  `NB_CapacityManager_Bootstrap` on `getSecret`. Niels deploys; continue in a later session.
- 2026-08-31 — **re-measured; both steps still outstanding, but the severity was overstated.**
  `checkMemberGroups` on `85553fa2-1343-4d6e-89e4-433fd51ba6a6` returns empty, so step (2) has not
  happened (the group holds 2 transitive members and was created 2026-08-25). `Fabric-ETL-DEV` is one
  commit behind `ebee979`, so step (1) has not either — and it now carries an uncommitted
  `Warehouse_Enriched_AX09`, so the sync needs a decision on that first.
  **The correction: TEST is not down and has not been.** Runs 08-24 → 08-28 all report `Failed`, and
  all of them built Raw, Enriched and Curated and refreshed the model — TEST's `Model` shows
  `Completed` at 2026-08-28 05:43, from the 04:30 run that "failed". Only the terminal
  `Fail Scale Up` marker fails; the underlying `errorCode` is still
  `Failed to resolve connection ''`. The pipeline's own message states the degradation: *"allowed to
  finish at the idle SKU - curated built, and the semantic model refresh ran without the memory it
  needs."* That behaviour came from `5a5df6f`, `abc9663`, `cd71032`, `0d10a6c` — four commits made
  after the 08-27 entry above and recorded nowhere until now.
  **So the open cost is refresh headroom, not lost data.** Reprioritise accordingly. Also noted: a
  TEST run started 2026-08-31 07:40 UTC, off the 04:30 schedule, trigger not established.
- 2026-08-31 (second pass) — **corrections to the entry above, all measured.**
  - **The 07:40 run FAILED at Raw, not at Scale Up.** `invokeType: Manual`, ended 09:07:05,
    `errorCode: "Operation on target AX09 failed: … AX09 table ingest failed"` /
    `"Operation on target Fail Raw failed: Raw load failed"`. **This is a new failure mode** — a
    stage that produces data — and it is distinct from the Scale-Up thread. Runs 08-24 through 08-28
    were all the Scale-Up/connection failure, so this is new today, not a week-long pattern. Needs
    its own investigation.
  - **DEV was never affected by the empty `CON-WI-Notebook`.** DEV has no Dev value-set override, so
    it resolves the base default `26b6988e-f53d-440b-852b-97c384cd5125` — a live connection, last
    credential use 2026-08-21. Only TEST's value set carries the empty string. Drop "DEV and TEST
    both still read empty".
  - **TEST's schedule is user-owned, not SPN-owned.** Schedule `16fb5ff0…`, enabled, Mon-Fri 06:30,
    owner **EXT_NSKC@carl-ras.dk**, `createdDateTime` **2026-08-30** — recreated the day before this
    check. Whatever SPN-owned schedule existed is gone. **This is a hardening regression**: the chain
    now depends on one person's account, which is the condition this task exists to remove.
  - **`PL_Update_SemanticModel` already points at `NB_Refresh_SemanticModel_Full` in DEV and TEST**
    (DEV notebookId `7b1df931…`, TEST `c70deb3f…`). The "still points at the old notebook
    `33e45f7b…`" line is **PROD-only** — PROD has no `_Full` notebook item at all.
  - DEV completed a full run 2026-08-20 12:19-14:00 and has not run since; its schedule is disabled
    and owned by EXT_NSKC. PROD's schedule is disabled and owned by **ext_sigr@carl-ras.dk**
    (Simon); PROD's model has **never** refreshed (empty refresh history); PROD's `VL_ConnectionId`
    lacks `CON-WI-Notebook` and the Marketo variables entirely.
  - **Correction to my own earlier note:** `Fabric_Key_Vault_Users` holds **2 members, not 0** —
    `c898431c-f141-4fe3-9a7b-3031618956b6` (Fabric-ETL-DEV) and
    `fa075892-6394-415c-b0a9-a25105e2f1a8` (Fabric-ETL / PROD). A plain `/members` call returns
    empty for a guest account; the `microsoft.graph.servicePrincipal` cast reveals them. TEST is
    still absent, so step (2) stands unchanged.
- 2026-09-09 — time: 52 min of session f0ca3d4e (08:00-11:42 UTC, rooted in own/MetaAtomic: MetaAtomic deployment, pipeline, schedule, PAT, stream matrix diagnosis) attributed here by Niels; the first 39 min go to 2026-09-09-carlras-metaatomic-implementation. Apply when 2026-09-09 is rolled up.
- 2026-09-09 — TEST Raw failure root-caused: PL_Ingest_Lakehouse_Raw_Marketo ran on a person's refresh token that Conditional Access rejects (AADSTS530036, since 09-04). Re-stamped to the SPN with fabric_identity.py, ran clean in TEST (a2764ae3, 3 min). Scale Up/Down: CON-WI-Notebook filled by the 10:09 DEV->TEST deployment; next failure moves to getSecret until TEST's workspace identity 85553fa2 joins Fabric_Key_Vault_Users (Carl Ras). New: PROD lakehouse SQL endpoints refuse every query (MWC token); first PROD raw load of AX09 completed 16:59 UTC.
- 2026-09-09 evening — PL_Execute_Raw ran green in TEST (66b7792f, 24 min, all four streams incl. GTM). Fail GTM added to the chain (8fae15f). PROD: all four raw layers loaded by hand (AX09 50 min, CVR, GTM, Marketo after NB_Table_PrimaryKeyMap_Marketo). Gate for enriched in PROD: lakehouse SQL endpoints refuse every query (MWC token).
- 2026-09-16 — brought onto the Progress shape (Progress + Needs from customer, `fno_task` / `customer_ask` set, `activity` blanked per CLAUDE.md task-always rule); no facts changed. Card: `customers/Carl-Ras/datahub/CONTEXT.md`.
- 2026-09-23 — rung-2 start diagnosed; max_rung=2 kept, reset is a per-run start_at_rung=1
- 2026-09-24 - CVR employee band. Report "Omsaetning pr. stoerrelse" shows the raw codes (ANTAL_20_49) and two (Tom) bars. Cause: the enriched CVR view has passed employees_interval through unchanged since 500acb5 (2026-05-07); a decode existed only as DEV drift on 08-12 and was erased when the view was rebuilt from git. The two (Tom) bars are data, not a visual setting: NULL (142,630 customers with no CVR row) and '' (11,192 matched with a blank band) both render as (Tom). Fixed in Fabric-ETL d659a2e/3db439b [GEN-012] - decode to Antal-prefixed band labels in viewtransform.CentralCompanyRegister, both empties collapse to one Unknown. Committed, NOT pushed; needs push + Update from git (Niels).
- 2026-09-24 - time to split at the review gate. This session is tagged here, but part of it was work in own/MetaAtomic (the consistency.sort_order_single DQ rule, commit 8cc1224) - an internal product change, not Carl Ras delivery. The CVR band fix and the DEV transform/model runs belong here; the MetaAtomic rule does not. Split it out of this task's line when 2026-09-24 is rolled up.
- 2026-09-25 — Curated table DDL matched to its views, Curated deployed to TEST; Enriched_AX09 deploy-build rejects fixed (GEN-014/015, `8ed2333`), wh_rules.py in pre-push; AX09 deploy pending
