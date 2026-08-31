---
title: Carl Ras — uncommitted workspace changes: git holds 40 AX09 ingest tables, every workspace runs 88-92
status: open
created: 2026-08-19
project: customers/Carl-Ras/datahub
owner: fabric-back
priority: high
blocked_by:
activity: AX09Import
fno_task:
source: direct
---

## What

Found 2026-08-19 while looking for `ledgerbudget`. It is in `Lakehouse_Raw_AX09` (1.6M rows) but in
no repo we hold. Two independent causes.

### 1. `PL_Ingest_AX09` has never been committed since 2026-04-29

`PL_Ingest_AX09` copies a **hardcoded table list** from the on-prem `Dynamics_Addon` SQL DB into
`Lakehouse_Landingzone_AX09`. Measured 2026-08-19 via `fab export` on each workspace:

| Where | Tables in the list | `ledgerbudget` |
|---|---|---|
| `Landingzone-ETL` repo (git) | **40** | no |
| `Landingzone-Code-DEV` workspace | **92** | yes |
| `Landingzone-Code-TEST` workspace | 88 | yes |
| `Landingzone-Code` (Production stage) workspace | 88 | yes |

Fabric's own git status for `Landingzone-Code-DEV` names the cause directly:

```
PL_Ingest_AX09           Modified   (workspace ahead of git)
PL_Ingest_AX09_Metadata  Added      (exists only in the workspace)
```

**Deployments were never the problem.** A Fabric deployment pipeline moves item definitions
*workspace → workspace*; it neither reads nor writes git. `Landingzone-Code Deployment` has run 18
times and carried `PL_Ingest_AX09` DEV→TEST→PROD as recently as 2026-06-15, which is exactly why all
three workspaces agree. Git fell behind because the last **commit from the workspace** on that item
was 2026-04-29 (`de837a4`), and every edit since — the 48 tables added, including `LEDGERBUDGET`,
`LEDGERTRANS`, `LEDGERTABLE`, `CONTACTPERSON`, `WMSPICKINGROUTE*`, the `ASSET*`/`TAX*`/`VEND*` sets —
was made in the workspace UI and left there.

DEV is also 4 tables ahead of TEST/PROD from an edit after the last deployment:
`ledgertablealternative`, `ledgertablealternativetrans`, `ledgertableinterval`, `wmsbilloflading`.

**The actual risk is the mirror image of a deployment.** An *Update from git* on
`Landingzone-Code-DEV` replaces the 92-table pipeline with the 40-table one and deletes
`PL_Ingest_AX09_Metadata`. A deployment afterwards carries that to TEST and PROD. Ingest for 52
tables then stops with no error — the pipeline still succeeds, it just copies less. Downstream that
is `enriched.GeneralLedgerTransactions` (113M rows), the Marketo↔AX09 bridge and `fact.PickingRoutes`.

`Fabric-ETL-DEV` carries the same class of exposure on one item: `PL_ScaleProcess_SP`, Modified,
uncommitted.

### 2. The Raw table set is never in git, by design (not a defect)

`PL_Ingest_Lakehouse_Raw_AX09_ChangedTables` > `Lookup tables in LandingZone` builds its table list
at runtime:

```sql
SELECT ... FROM INFORMATION_SCHEMA.TABLES a JOIN INFORMATION_SCHEMA.COLUMNS b
WHERE UPPER(b.COLUMN_NAME) = 'RECID' AND a.TABLE_TYPE = 'BASE TABLE'
```

Every landing-zone table carrying a `RECID` is ingested. So Raw holds whatever the landing zone
holds and no artefact in the repo lists it. That is Atomic working as intended, but it means **the
repo cannot answer "what data do we have"** — only the lakehouse can. Same boundary the MetaAtomic
lineage work hit (`2026-08-03-metaatomic-consolidation`) and solved by querying the lakehouse.

## To do

1. ~~Get git and DEV onto the running 88-table list.~~ **Done 2026-08-20** — see Log.
2. ~~**Awaiting Niels: Update from git on `Landingzone-Code-DEV`, taking the incoming side.**~~
   **Done — verified 2026-08-31.** The Fabric git-status API reports `Landingzone-Code-DEV` synced at
   `d706f41` with **0 changes**, and `d706f41` contains `074ea1c`, so the 88-table list is live in
   the workspace. Git and DEV agree.
3. ~~**Commit `PL_ScaleProcess_SP` from `Fabric-ETL-DEV`**~~ **Done** — landed in `2213b8c`; it no
   longer appears in that workspace's git status. **But the same class has recurred:**
   `Warehouse_Enriched_AX09` is now Modified/uncommitted in `Fabric-ETL-DEV` (verified 2026-08-31),
   and `Fabric-ETL-DEV` is one commit behind (`ebee979`) — so an Update from git there would discard
   the workspace change. Commit or discard it deliberately first.
4. **Sweep the remaining git-connected workspaces** for uncommitted changes — `Semantic-Model-DEV`,
   `Sales-DEV`, `Fabric-TEST` were not checked.
5. **Decide on the five orphan landing-zone tables** — `LEDGERTABLEINTERVAL`,
   `LEDGERTABLEALTERNATIVE`, `LEDGERTABLEALTERNATIVETRANS` (last written 2026-06-29),
   `WMSBILLOFLADING` (2026-06-25), `DIRORGANIZATIONDETAIL` (2026-05-07). They are in no active list,
   nothing refreshes them, and Raw ingests them nightly anyway because they carry a `RECID` — so
   Raw serves May/June data as current. Either add them to the list or remove them from the landing
   zone.
4. **Make it observable.** `workspaces/{id}/git/status` returns this in one call. A scheduled check, or
   a gate in `tools/fabric_release.py` that refuses to release while a source workspace has
   uncommitted changes, closes the hole. Cheap and worth doing.

## Why

The workspace rule is that nothing exists in a Fabric environment except as derived from the repo.
Here the repo is a stale snapshot of one item and has been for four months, and the mechanism meant
to restore the rule — Update from git — is what would destroy the running configuration.

## Log
- 2026-08-19 — found while scoping `2026-08-19-carlras-ax09-budgetledger-curated`. Exported
  `PL_Ingest_AX09` from all three workspaces and diffed against the repo; read the deployment
  pipeline's 18-operation history and both DEV workspaces' git status. First pass mis-stated the
  direction (repo compared against TEST/PROD and labelled "DEV"); corrected after exporting the DEV
  workspace itself. Nothing changed in Fabric or in the customer repos.
- 2026-08-20 — Niels ran Commit from workspace on `Landingzone-Code-DEV`, which pushed the debug
  state to git (`80981e2`: 1 active table, `LEDGERTABLEINTERVAL`); it also brought
  `PL_Ingest_AX09_Metadata` into git for the first time. Corrected in `074ea1c` (approved, pushed):
  the `sqlReaderQuery` replaced with PROD's running definition verbatim, 1 → 88 active tables, one
  line changed, CRLF and the `logicalId` notebook reference preserved. Git is now the truth.
  Remaining: Update from git into `Landingzone-Code-DEV`, taking the incoming side.
- 2026-08-31 (second pass) — **two corrections and one finding that changes item 4's design.**
  - **My "an Update from git would discard `Warehouse_Enriched_AX09`" was WRONG.** That item shows
    `workspaceChange: Modified, remoteChange: null, conflictType: None`, and `ebee979` changes exactly
    one file (`VL_ConnectionId/valueSets/Test.json`). The pending sync does not touch the warehouse.
    It still needs its own commit — but it is not at risk from the pull, and the pull need not wait
    for it.
  - **Four-way table count now agrees exactly: 88 everywhere** — repo (`d706f41`), DEV, TEST and
    PROD, with `LEDGERBUDGET` present in all four and all six pairwise name-set diffs empty. Items 1
    and 2 close for good. `PL_Ingest_AX09_Metadata` is in the repo and in DEV, absent in TEST and
    PROD (not yet promoted, not a defect) — which makes the customer-node `CLAUDE.md` line calling
    it "in no repo we hold" stale.
  - **Item 4 finding — a git-status gate would NOT be sufficient.** `Warehouse_Curated` in
    Fabric-ETL-DEV reports **clean** in `git/status` while three of its views demonstrably differ
    from git (the 13-month GL/Sales/Inventory hand-patch, verified by `OBJECT_DEFINITION` vs the repo
    file — see `2026-08-17-carlras-curated-data-loss-windows`). So Fabric's own drift signal misses
    warehouse-internal changes. Build the gate, but do not treat a clean `git/status` as proof a
    workspace matches git.
  - **Sweep completed:** Landingzone-Code-DEV clean; Semantic-Model-DEV clean (`6be70e64`); Sales-DEV
    clean (`e333a817`); Fabric-ETL-DEV two items as above. **`Fabric-TEST` is not visible to
    `EXT_NSKC@carl-ras.dk` at all** — an access gap, not an API error, so that repo stays unchecked.
  - **Item 5 confirmed:** all five orphan tables still in the landing zone, still absent from the
    88-table list, still ingested nightly by the RECID rule. Staleness today: 63 days for the three
    ledger tables and `WMSBILLOFLADING`, **116 days** for `DIRORGANIZATIONDETAIL`. Raw serves them as
    current. Needs your call: add to the list, or drop from the landing zone.
- 2026-08-31 — **verified closed for `Landingzone-Code-DEV`.** Fabric git-status API: synced at
  `d706f41`, 0 changes, and `074ea1c` is an ancestor — the 88-table list is live in the workspace and
  git is the truth. `Semantic-Model-DEV` also clean (0 changes). Step 3's `PL_ScaleProcess_SP` is
  committed. **Task stays open on steps 4-5 and the recurrence:** `Warehouse_Enriched_AX09` is now
  Modified/uncommitted in `Fabric-ETL-DEV`, which is the same failure mode one item further along —
  and that workspace is one commit behind (`ebee979`), so a sync would discard it. Step 4 (make it
  observable — a `git/status` gate in `fabric_release.py`) would have caught this without a manual
  sweep; this is the second occurrence, which is the argument for building it.
- 2026-08-20 — noted for the record: a separate metadata-driven ingest solution for Atomic is being
  built by someone else. If it lands, the hardcoded list in this pipeline is superseded. The
  observation still holds that `TableMetaData_AX09` is `OverwriteSchema`-refreshed and therefore
  cannot host a load/skip flag — declared intent needs its own table, seeded from git, the way
  `Lakehouse_Util.rawtablekeymap_<source>` already is.
