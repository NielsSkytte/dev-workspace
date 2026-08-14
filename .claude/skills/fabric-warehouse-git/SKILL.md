---
name: fabric-warehouse-git
bundle: custom
description: >
  How a Microsoft Fabric Warehouse behaves as code in a git-connected workspace, and what
  breaks on "Update from git". Use this skill whenever a schema change to a Fabric
  Warehouse has to travel through git - adding, removing, renaming or reordering a column
  on a warehouse table or view - and whenever a source-control sync fails or silently
  destroys data. Trigger on "Update from git failed", "commit from workspace",
  "ObjectNotFoundInCollection", "columns 'X' not found in etl or database", a table name
  with a "(1)" suffix in an error, "DmsImportDatabaseException" with "Invalid column name"
  on a sync, "data in the following tables will be deleted", a warehouse table that came
  out empty after a sync, `xmla.json`, `.sqlproj`, `Microsoft.Build.Sql`, DacFx rebuilding
  a table instead of altering it, column order / ordinal changes, the
  "Auto Generated (Do not modify)" header and its hash, drift between a workspace and its
  branch, or validating .sql files before committing them. Also trigger on "can I drop
  this column", "will this sync lose data", "why is source control showing the whole
  warehouse as one item", and on planning a multi-warehouse schema change.
  This skill owns the WAREHOUSE-AS-CODE contract and git-sync failure modes inside one
  workspace. Promoting items DEV -> TEST -> PROD through a deployment pipeline is
  `fabric-deployment`. Workspace structure, branch model and the git-not-`fab import`
  authoring rule are `pingala-fabric-platform`. Renaming an item is `fabric-rename-entity`.
  Row-count reconciliation after data moves is `medallion-migration-validation`.
---

# Fabric Warehouse as code: the git-integration contract

Evidence base: Carl Ras `Fabric-ETL`, Azure DevOps, workspace Fabric-ETL-DEV, 2026-08-13/14.
Removing one per-row validation column (`PIN_RowCheck`) from 28 views and 29 table DDLs took
**six failed "Update from git" attempts over two days** and cost 1.85M permanently lost rows.
Every rule below is from that run unless marked otherwise.

## Core principle: one warehouse, three synchronised artifacts

A git-connected warehouse serialises to a folder `<Name>.Warehouse/` containing:

| Artifact | What it is |
|---|---|
| `<schema>/Tables/<T>.sql` | the physical table DDL |
| `<viewschema>/Views/<T>.sql` | the view that produces it |
| `xmla.json` | the **default semantic model** definition - every table and every column, twice |
| `<Name>.sqlproj` | the DacFx project file, pinning the `Microsoft.Build.Sql` SDK version |
| `.platform` | item identity |

**The rule that costs the most days:** a column change is **three files, not two**. The view,
the table DDL, *and* `xmla.json`. Miss `xmla.json` and Update from git is blocked outright.

### The repo is an input for some fields and an output for others

Every file above is **produced by serialising the warehouse**. Whether editing one in git
actually changes anything depends on the field, and the two cases look identical in a diff:

| | Edit it in git and... |
|---|---|
| **Input** - the import consumes it | the warehouse changes. Table DDL, views, and `xmla.json` behave this way: a stale `xmla.json` blocks the import, and fixing it is what unblocked ours. |
| **Output** - the workspace owns the value and re-emits it | nothing changes. The branch just goes out of step until the next commit-from-workspace overwrites your edit. **Confirmed for the `.sqlproj` SDK version** (failure 5). |

So "I changed it in git and pushed" is not evidence the warehouse changed. **Confirm against the
warehouse, not against the branch** - and treat an item that flips to a pending Change straight
after a successful Update from git as the signature of an output field: the workspace re-serialised
and disagreed with what you wrote.

Only the SDK version is confirmed output-side. Do not assume the rest of the `.sqlproj` behaves
the same way without testing it - the cheap test is the one used in failure 5: change one
warehouse, on a clean tree, with nothing else in flight.

> **The docs are unreliable on this specific surface - verify against the tenant.** Two
> contradictions in one change: MS states `xmla.json` is excluded from git integration and
> ignored on sync (a stale `xmla.json` is exactly what blocked our import, and fixing it is what
> unblocked it); and MS documents two remedies for a stale `.sqlproj` SDK pin, neither of which
> works here (failure 5). Reason from the error and from a `#temp`-table probe, not from the
> page.

---

## Failure catalogue

### 1. `ObjectNotFoundInCollection` naming a table with a `(1)` suffix

**Symptom.**

```
Workload Error Code     ObjectNotFoundInCollection
Workload Error Message  Table 'AlternativeChartOfAccount(1)' columns
                        'PIN_RowCheck' not found in etl or database.
```

**Do not diagnose this as a DacFx shadow table.** We did, twice, and burned two attempts on it.
The `(1)` is a **table name inside `xmla.json`**.

**Why the suffix exists.** The default semantic model lists *both* the physical table and the
view that builds it, and a semantic model's table namespace is flat while SQL's is
schema-qualified. So `enriched.AlternativeChartOfAccount` and
`viewtransform.AlternativeChartOfAccount` collide, and whichever was added second gets `(1)`.
Verified across every warehouse in the repo:

| Warehouse | Declarations | Real objects | Pattern |
|---|---|---|---|
| Enriched AX09 | 62 | 31 | 31 `viewtransform` (plain) + 31 `enriched` (all `(1)`) |
| Curated | 56 | 28 | `dim`/`fact`/`bridge` vs `viewdimtransform`/`viewfacttransform`/`viewbridgetransform`; the suffix falls on either side |
| Enriched CVR | 2 | 1 | same pair |
| Enriched GTM | 1 | 1 | view only, no physical table -> no duplicate |

The suffix is **not** attached to a fixed kind (table or view) - it goes to whichever entry was
serialised second. So do not filter on it; read each entry's `sourceLineageTag`, which carries
the real `[schema].[object]`.

**Cure.** Remove the column from **both** `xmla.json` entries for that object, in the same commit
as the view and the DDL. Present since 2026-04-13 and growing in lockstep with the table count -
this is systematic behaviour, not drift to be cleaned up.

### 2. Dropping a NOT NULL column EMPTIES the table

**Symptom.** The sync reports success, the schema is right, the table has zero rows.

**Cause.** DacFx cannot `ALTER` away a NOT NULL column, so it **rebuilds**: creates a shadow
table, copies rows using the OLD column list, and fails on the column that no longer exists. The
schema deployment still completes and leaves no orphan, so nothing looks wrong - but every
affected table comes out empty.

**Cure - the asymmetry that makes this worth doing.** Dropping the column *yourself* first is an
in-place metadata change; letting DacFx drop it triggers a full rebuild. So run
`ALTER TABLE ... DROP COLUMN` in the target warehouse **before** Update from git. The sync then
finds nothing to change and the table is untouched.

Verified 2026-08-14: `ALTER TABLE ... DROP COLUMN` on a NOT NULL `varchar` is supported in Fabric
Warehouse and preserves the remaining rows (proved on a session-scoped `#temp` table, see
*Techniques*).

### 3. Column ORDER triggers the same rebuild

`ALTER TABLE ... ADD` can only **append**. If git declares the new column mid-table, the ordinals
disagree, DacFx rebuilds to fix them, and you lose the data anyway.

**This is acceptable when a CTAS rebuild follows** - `sp_CreateTableAsSelect` does
`SELECT *` from the view, so the next chain run restores git's intended order by itself. Same
columns, same types, only the ordinal differs in the meantime.

Verified: `ALTER TABLE ... ADD` of nullable columns is metadata-only - 0.2s each against a
12,340,951-row table, row count unchanged.

### 4. Cross-warehouse dependencies are NOT sequenced - and the whole import rolls back

**Symptom.** Adding a column in Enriched and consuming it in Curated **in the same commit**:

```
Workload Error Code     DmsImportDatabaseException
Workload Error Message  Error occured during import database for the Datawarehouse '...'.
                        File: viewfacttransform/Views/SalesTransactions.sql,
                        Error: Invalid column name 'ContactPersonId'.
```

**Cause.** Fabric imports each warehouse item independently and does not order them
("Cross-item dependencies between warehouses and SQL analytics endpoints aren't currently
supported" - Fabric docs, *Limitations in source control*). Curated compiles against an Enriched
column that has not landed yet.

**Nothing is applied - the import rolls back whole, including the half that would have worked.**
An all-or-nothing failure across warehouses is the signature.

**Cure.** Pre-add the column in the producing warehouse by hand (metadata-only, see 3), then
sync. Or split into two commits and sync twice, producer first.

**Sibling.** The deployment-pipeline version of this - three-part names across databases, cured
by promoting in dependency order - is `fabric-deployment` > failure 1. Same class, different
mechanism: that one is about a *missing object* at promotion, this one about a *missing column*
at git import.

### 5. The stale `.sqlproj` SDK pin - a red herring, and you cannot fix it from git

`<Sdk Name="Microsoft.Build.Sql" Version="..." />` sits at whatever the warehouse was created
with. All five warehouses here are on `0.1.19-preview`; current is `2.2.0`, and **MS docs flag
any version starting `0.1.` as out of date and a cause of commit and update failure.** So it
looks like the answer. Twice over, it is not.

**It was not our problem.** The bump did not fix the sync - `xmla.json` did. Check the version,
note it, and keep looking.

**And a git-side edit does not stick.** Confirmed by controlled single-warehouse test, three
independent observations (recorded in `08a31c3`):

| # | What | Result |
|---|---|---|
| 1 | `7fbdc1f` set all five warehouses to `2.2.0` | Fabric's next commit-from-workspace `965a8ba` **reverted all five** to `0.1.19-preview` |
| 2 | `e99db04` set **one** warehouse only - `Warehouse_Enriched_GTM`, one view and no physical tables so a rebuild could not cost data - branch and workspace clean, nothing else in flight | On Update from git the item **flipped to a pending Change immediately**: Fabric's serialisation of the workspace still produced `0.1.19-preview` |
| 3 | `1fbcb2c` - commit from the workspace | Wrote `0.1.19-preview` back into the repo on its own |

Observation 1 alone was inference: that bump went out alongside the `xmla.json` fix, the AX09
view edits and the Curated outbound work, so the revert was not cleanly attributable. Test 2
isolated it - single warehouse, clean tree, nothing else moving - and the warehouse reported a
difference against the branch the *moment the branch disagreed with it*.

> **The mechanism.** The SDK version is a property of the warehouse **in the workspace**. The
> `.sqlproj` in git is an **output** of serialising that warehouse, not an input to it. Writing
> a different value into the repo does not change the warehouse - it puts the branch out of step
> until the next commit-from-workspace overwrites it.

Microsoft documents two remedies and **neither moved it on this tenant**: editing the `.sqlproj`
in git directly (test 2 - reverts), and committing from the workspace to regenerate the file at
the current SDK version (test 3 - regenerates at the OLD version). What *does* move it is
unknown.

**So: do not spend a cycle on this.** Record the version, do not edit it in git, and treat
`0.1.x` as a background condition rather than a lead.

**Revisit only on this signal:** a sync that fails to **parse** modern T-SQL the old SDK predates
- `IDENTITY`, `CLUSTER BY`. A parse failure on current syntax is the one symptom the version
plausibly explains; anything else is not it.

### 6. A hand-edited view leaves a stale `Auto Generated` hash

Serialised views carry a header `-- Auto Generated (Do not modify) <hash>`. Edit the SQL by hand
and the content is right but the hash is not, so the file stays `Modified` until Fabric rewrites
the header itself.

**The hash derives from Fabric's parsed model, not from the file text. It cannot be recomputed
externally.** No SHA-256 variant reproduces it - tested, including against files we never
touched, so it is not a matter of finding the right normalisation of our edit.

**Therefore any hand-edited .sql needs exactly one normalising commit-from-workspace to settle.**
Observed: 74 files, and in every view the only change was the hash line. Plan for that commit and
tell the user to expect it; do not try to precompute the hash, and do not read the resulting diff
as a defect. (Same class as the normalising commit after a new item arrives -
`pingala-fabric-platform`.)

### 7. Warehouse source control is item-level, so drift is invisible

The Source control panel shows one row, `Warehouse_X`. It never shows objects. A single view can
differ between workspace and git **for months** with the panel showing nothing until you open
*Review changes* - we found one uncommitted since 2026-07-03.

Update from git is also **all-or-nothing across the branch**: you cannot update selected items.

And: commit is offered only to a **new branch** when the workspace is behind. That is normal
Fabric behaviour, not a fault - stop investigating it.

---

## The data-loss decision rule

### First, the reassurance: a failed sync loses OBJECTS never, CONTENTS sometimes

"Will a failed Update from git delete my views?" is the natural fear and the answer is **no**.

Verified by full live-vs-git inventory after six failed syncs and one successful one - **zero
object loss**:

| Warehouse | Schema | Live / git |
|---|---|---|
| Enriched AX09 | `viewtransform` / `rowcheck` / `enriched` | 30/30, 28/28, 31/31 |
| Curated | `viewdimtransform` / `viewfacttransform` / `viewbridgetransform` / `viewoutboundtransform` | 17/17, 8/8, 3/3, 1/1 |
| Curated | `dim` / `fact` / `bridge` / `outbound` | 17/17, 8/8, 3/3, 1/1 |

**Failed syncs roll back cleanly and do not drop objects.** The damage is confined to table
**contents**, and only where DacFx rebuilds a table (failures 2 and 3). Keep the two apart when
reporting risk: a failed sync costs time; an accepted rebuild warning costs rows.

### Then, the actual decision

Fabric warns "data in the following tables will be deleted". Answering it correctly is the
difference between a 17-minute rebuild and permanent loss.

**Accept when the table is derived and rebuildable.** Enriched and Curated content is disposable
by design - the transform chain regenerates it.

**Refuse when the table has no rebuild path.** A table with **no `viewtransform` view** is never
regenerated by the chain, so its rows are gone permanently. We lost **1.85M rows from
`enriched.DeliveryAddress`** exactly this way.

**The check, before accepting any such warning:** for every named table, confirm a view exists
that produces it. No view, no rebuild, no acceptance.

---

## Techniques

### Validate every changed .sql against the live warehouse - `SET PARSEONLY ON`

`SET PARSEONLY ON` **is supported in Fabric Warehouse**. It parses without creating anything, so
you can validate a whole changeset against the real warehouse before committing. We validated 92
files this way. Use it as the pre-commit gate on any bulk edit of serialised SQL.

### Prove DDL behaviour with a session-scoped `#temp` table

Questions like "does DROP COLUMN preserve rows here?" are answerable in seconds, on the real
engine, without dirtying source control - `#temp` tables are session-scoped and never serialised.
Prefer this over reading docs about DacFx behaviour; the docs were wrong about `xmla.json`.

### Detect workspace-vs-git drift programmatically

Compare `OBJECT_DEFINITION(OBJECT_ID('schema.view'))` against the repo file, normalising away the
`Auto Generated` header and comments.

**This is the only programmatic route**: the Fabric `git/status` API is **not available to a
service principal** - it returns `GitCredentialsNotConfigured`. Do not build a drift check on it.

### Scripting bulk edits: preserve CRLF and BOM

Reading serialised files with universal newlines and writing back LF turned a **421-line diff into
a 6,009-line whole-file rewrite**. Read and write bytes, or pin `newline=''` and keep the BOM.

For `xmla.json`, `json.dumps(indent=2)` **round-trips Fabric's serialisation byte-identically**,
so targeted JSON edits produce clean, reviewable diffs. Verified on this repo.

---

## Procedure: changing a column in a git-connected warehouse

1. **Edit three files per object** - the view, the table DDL, and *both* `xmla.json` entries
   (plain and `(N)`).
2. **Validate** every changed .sql with `SET PARSEONLY ON` against the live warehouse.
3. **Write a pre-deploy script** for the target environment: pre-`DROP COLUMN` what is being
   removed (failure 2), pre-`ADD` what a downstream warehouse will consume (failure 4). Make it
   idempotent and a no-op on an environment already at those commits. Template:
   `references/predeploy-template.sql`.
4. **Run the pre-deploy script in the target warehouse**, and confirm its check query returns all
   zeros.
5. **Update from git.** It should now be close to a no-op on the affected tables.
6. **Verify row counts survived**, then run the transform chain to restore any table that was
   rebuilt and to correct column ordinals.
7. **Expect one normalising commit-from-workspace** if any view was hand-edited - it rewrites the
   `Auto Generated` hash and nothing else (failure 6).

**Do not detour into the `.sqlproj` SDK version.** It is the most inviting-looking dead end here:
a `0.1.x` pin is documented as a cause of sync failure, it was not ours, and it cannot be fixed
from git anyway (failure 5).

---

## Boundaries

- **Promoting between environments** (deployment pipelines, variable libraries, identity
  re-stamping, seeding) - `fabric-deployment`. A git sync and a deployment are different
  mechanisms with different failure modes; do not transfer rules between them.
- **Workspace structure, branch model, and why new items go in via git rather than
  `fab import`** - `pingala-fabric-platform`.
- **Renaming or moving a git-connected item** - `fabric-rename-entity`.
- **Reconciling row counts after data has moved** - `medallion-migration-validation`.
- **Per-customer names** - which warehouses, which schemas, which transform pipeline - belong in
  that customer's `CLAUDE.md`, never here.
