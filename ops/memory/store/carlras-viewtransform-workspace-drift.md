---
id: carlras-viewtransform-workspace-drift
ts: 2026-08-13T08:29:46Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: session:d96c18e1-0555-475f-a4be-0c76a71e9ca1
tags: [project, fabric, source-control, revert]
status: distilled
description: "Carl Ras AX09: ChartOfAccountToAlternativeChartOfAccount differs between the DEV workspace and git — the workspace holds uncommitted work, both versions preserved so it can be reverted"
---

**RESOLVED 2026-08-13** — Niels committed from the workspace as `580c8b0` ("old change to
ChartOfAccountToAlternativeChartOfAccount popped up, now committed"). The committed file was
verified byte-equivalent to the live DEV definition, so git and the workspace now agree and the
accidental-revert hazard is gone. The commit also carried `xmla.json`. Record kept for the revert
material below and for the source-control lesson.

`viewtransform.ChartOfAccountToAlternativeChartOfAccount` in **Fabric-ETL-DEV** did not match the
`.sql` file in the `Fabric-ETL` repo. Found 2026-08-13 while validating a replacement for
`PIN_RowCheck`. **The workspace copy was the newer one and was not in git.**

Swept all 30 `viewtransform` views by comparing `OBJECT_DEFINITION` against the repo files:
**29 match, this one differs.** No orphans in either direction. Drift is contained to this view,
in DEV. TEST and PROD not checked.

## Revert material

**Primary source is git, not the files below.** Both versions live in `Fabric-ETL` history:

- pre-commit (July, the buggy 2-table version) — `git show 1baffda:"02 - Enriched/AX09/Warehouse_Enriched_AX09.Warehouse/viewtransform/Views/ChartOfAccountToAlternativeChartOfAccount.sql"` (110 lines)
- the workspace version Niels committed 2026-08-13 — `git show 580c8b0:"<same path>"` (112 lines)

Convenience copies also sit at `customers/Carl-Ras/datahub/data/drift-2026-08-13/` — but note
`data/` is **gitignored**, so those are local-only and not backed up. Do not rely on them:

- `ChartOfAccountToAlternativeChartOfAccount.WORKSPACE.sql` — the live DEV definition (112 lines)
- `ChartOfAccountToAlternativeChartOfAccount.GIT.sql` — the repo version (110 lines)
- `drift.diff` — unified diff, GIT (-) vs WORKSPACE (+)

Pulled with `SELECT OBJECT_DEFINITION(OBJECT_ID('viewtransform.<name>'))`. Note that
`OBJECT_DEFINITION` omits the `-- Auto Generated (Do not modify) <hash>` header Fabric writes on
serialisation; that line has to be restored if the workspace version is ever written back as a
repo file.

## What differs

| | git | DEV workspace |
|---|---|---|
| METADATA `PrimaryTable` | `ledgertableinterval` | `ledgertablealternativetrans` |
| driving table | `ledgertableinterval` | `ledgertablealternativetrans` |
| join between the two | `LEFT JOIN ledgertablealternativetrans` | `FULL OUTER JOIN ledgertableinterval` |
| `ACCOUNTTABLEID = 223` | in `WHERE` | moved into the `JOIN` |
| `SCDcurrent` filter | on `ledgertableinterval` | on `ledgertablealternativetrans` |
| `PIN_DataAreaId`, `PIN_RecId` | from `ledgertableinterval` | from `ledgertablealternativetrans` |
| `PIN_RowCheck` expectation | 2-table join → 11,930 | 3-table join → 12,787 |

The repo version drops `ledgertablealternativetrans` rows with no matching interval; the workspace
version keeps them. Row counts 11,930 vs 12,787.

**Read on the merits: the workspace version looks like the fix, the repo version like the bug** —
if the intent is "every alternative chart-of-account line, mapped to accounts where a mapping
exists". Inference, not confirmed by the author.

## Provenance

Git history for the file is a single commit — `1baffda`, **2026-07-03, Simon Reinholdt Gath**,
"Committing 7 items from workspace". That is also the last commit to touch the AX09 warehouse at
all, so the repo has been frozen since 3 July while the workspace moved on.

The workspace version carries a commented-out debug filter,
`--AND [ledgertablealternativetrans].[ACCOUNTNUM] = '04100'`, and switches the changed regions from
the file's space indentation to tabs. Both are hallmarks of hand authoring in the SQL editor.
Niels's read (2026-08-13): almost certainly Simon's work, made just before he went on **maternity
leave**. He is not to be contacted about it. Niels confirms he did not make the change himself.

Hand authoring is not the only possible delivery route — `fab import -f`, an API
`updateDefinition`, or a deployment pipeline run *into* DEV would each move the workspace without
touching git.

## Why it never showed in source control

Two documented facts, then one inference.

- Fabric warehouse git integration tracks changes at the **item** level, not per object
  ("Selective commits at the warehouse level aren't currently supported"). The panel shows
  `Warehouse_Enriched_AX09` as one pending change — the view name only appears inside
  *Review changes*. So there was never a line item naming this view to notice.
- Warehouse git integration is in **preview**, and schema extraction is DacFx-based and runs
  during sync / branch-out workflows rather than continuously.
- *Inference:* running `CREATE VIEW`/`CREATE TABLE` DDL in DEV on 2026-08-13 marked the warehouse
  as a pending change, and the extraction that followed surfaced every accumulated difference —
  including this one, sitting there since July. Not proven; it is equally possible the item had
  been showing as modified and the cause was never opened.

## Guardrail

**Do not "Update from git" on `Warehouse_Enriched_AX09` in DEV.** Update always syncs the entire
branch and cannot be done selectively — it would overwrite the workspace copy with the July file
and silently revert the change. Commit-from-workspace is the safe direction, but only once someone
confirms which version is correct.

Also note the current data reflects the **workspace** version: `enriched.ChartOfAccountToAlternative
ChartOfAccount` was last built 2026-08-07 13:43 with 12,787 rows.

Found while replacing `PIN_RowCheck` with a post-load check (`rowcheck` views +
`transform.sp_RowCheck` + `transform.RowCheckLog`). That work also established that 4 enriched
tables carry a `Failure` verdict nothing has ever read: `DeliveryAddress`,
`GeneralLedgerTransactions`, `SalesInvoiceTransactions`, `SalesLineTransactions`. Not yet written
up as its own record.
