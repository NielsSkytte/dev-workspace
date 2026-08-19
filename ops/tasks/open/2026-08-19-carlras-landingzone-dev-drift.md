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

1. **Commit the workspace state** — `PL_Ingest_AX09` (Modified) and `PL_Ingest_AX09_Metadata` (Added)
   from `Landingzone-Code-DEV`, and `PL_ScaleProcess_SP` from `Fabric-ETL-DEV`. Customer repos: needs
   Niels's approval before pushing. **Until then, do not run Update from git on either DEV workspace.**
2. **Deploy DEV→TEST→PROD afterwards** so the 4-table DEV lead lands, or revert it if unintended.
3. **Sweep the remaining git-connected workspaces** for uncommitted changes — `Semantic-Model-DEV`,
   `Sales-DEV`, `Fabric-TEST` were not checked.
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
