---
title: Carl Ras — convert the semantic model from Import to Direct Lake (composite on OneLake)
status: in-progress
created: 2026-08-18
project: customers/Carl-Ras/datahub
owner: semantic
priority: high
blocked_by:
activity:
fno_task:
source: session
---

## What

Replace the Import semantic model with `Model_OneLake` — a Direct Lake **on OneLake** composite over
`Warehouse_Curated`. Built and verified in DEV on 2026-08-18. Full assessment, every measurement and
every MS Learn citation: `customers/Carl-Ras/datahub/design/DIRECTLAKE_CONVERSION_ASSESSMENT.md`.

Shape: 25 tables Direct Lake, 3 Import (`Date`, `Alternative Chart of Account`, `Last Refresh` —
they carry the two calculated columns and the Power Query timestamp), 6 calculated/parameter tables,
177 measures, 55 relationships, 3 calculation groups.

## Why

The Import model can no longer refresh. On 2026-08-18 the DEV model failed at 122 s with
`consumed 4665 MB, memory limit 4661 MB`; TEST fails the same way and `NB_Refresh_SemanticModel_Full`
exists only to work around it with an adaptive batch-halving ladder. Direct Lake removes the rebuild
entirely — framing is metadata only.

## Measured in DEV, 2026-08-18

| | Import | Direct Lake composite |
|---|---|---|
| refresh / frame | **fails, out of memory** | **21.8 s** |
| all 177 measures evaluate | — | 177 OK, 0 failed |
| `Sales \| Revenue \| Std` vs SQL | — | within 0.011 kr on 2.8 bn |
| report render, median of 3 (Salg / Finance / Kunde) | 11.0 / 10.0 / 11.0 s | 9.1 / 9.0 / 12.0 s |
| Inventory Transactions rows carried | 3.3M | 17M |
| cold query after a rebuild | — | 1.1 s simple, 5.8 s heavy |
| parquet files per table (guardrail 1,000) | — | max 84 |
| curated size on OneLake (guardrail 10 GB) | — | 3.15 GB |

## Done

- `Model_OneLake` in Semantic-Model-DEV, authored via git (`Semantic-Model` `25d830d`, `44da1b0`).
- Five Sales-DEV reports cloned and rebound, suffixed `[OneLake]`; originals untouched.
- `CON-WI-SQL-Warehouse_Curated_DEV` connection; Semantic-Model-DEV's workspace identity granted
  **Contributor on Fabric-ETL-DEV** (a WI connection is refused without a role in the workspace
  holding the data).

## To do

1. **Framing step at the end of `PL_Transform_Curated`, with retry and backoff.**
   `PL_Update_SemanticModel` becomes a framing call instead of a memory-managed import refresh.
   Retry is required — framing immediately after a rebuild fails ("A direct lake table ... is not
   found", and "source tables do not exist or access was denied").
2. **Leave "Keep your Direct Lake data up to date" ON.** With drop-create the old files are deleted,
   so disabling it extends the failure window from ~25 s per table to the whole build. This is the
   opposite of the usual MS guidance and the reasoning is in the assessment.
3. **Deployment rules per target stage — two per stage.** Direct Lake models do **not** autobind;
   without rules, TEST would deploy still reading Fabric-ETL-DEV, silently. One rule for the SQL
   source (Import tables), one for the ADLS/OneLake source (Direct Lake tables).
4. **Per-stage identity grants:** Semantic-Model-TEST's workspace identity → Contributor on
   Fabric-ETL-TEST, and the same for PROD.
5. **Decide the GL window** now that memory is no longer the constraint. 3 years costs ~2.1 GB on
   OneLake and fits the current SKU; full history is ~10.3 GB and does not.
6. **Agree with Mads that derived columns go in the curated view, not the model.** Direct Lake accepts
   no calculated columns. Two exist today and one arrived on 2026-08-05 as ordinary report work; the
   composite keeps them alive on Import tables, but that is a workaround, not a policy.
7. Repeat the report render test across a working day — two Direct Lake outliers (16.7 s, 31.3 s) had
   no Import equivalent and the cause is not established.

## Open

- The workspace is git-connected to `main`, but `main` refuses direct commits, so anyone editing a
  model in the DEV workspace cannot commit it back. `Model` has been sitting with uncommitted
  workspace changes because of this. Not a Direct Lake problem, but it blocks Update from git.
- Related: `2026-08-18-carlras-atomic-ctas-merge` (the drop-create pattern behind the 25 s windows).

## Log
- 2026-08-18 — created. Model built, verified and benchmarked in DEV; reports cloned and rebound.
