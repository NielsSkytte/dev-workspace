---
title: Consolidate lineage engine + Tystofte source extraction into MetaAtomic
status: in-progress
created: 2026-08-03
project: own/MetaAtomic
owner: architect
priority: high
blocked_by: (unblocked 2026-08-04 — v1 delivered; steps 0-3 and 6 done, step 1 commit awaiting owner)
activity:
fno_task: none
customer_ask: none
waiting_on:
resume_on:
source: direct
---

## What

Make `own/MetaAtomic` the single home for the metadata/lineage capability by moving the two working
solutions into it, and turn the customer projects into deployments that import it.

Sequence (owner's ordering, 2026-08-03: finish the Element Logic build → move → then test on a new
customer):

0. **Finish the initial Element Logic setup** — in place, in `customers/ElementLogic`. Not part of
   this task; this task waits on it.
1. **Settle the loose work.** Commit or resolve the uncommitted engine changes in
   `customers/ElementLogic` (`model.py`, `html_report.py`, `graph_builder.py`, `enrich.py`,
   `cli.py`, untracked `tmdl_semantic.py`). Nothing moves until this is clean.
2. **Move the engine.** `lineage_engine/` → `own/MetaAtomic/`. Behaviour unchanged. Retire
   `framework/canonical_schema.py` and `framework/normalize_staging.py`.
3. **Re-point LineageDocumentation.** It keeps config, `Input/`, `out/`, notebooks and customer
   overrides; it holds no engine code and imports MetaAtomic. Verify the full Element Logic run still
   reproduces (19,996 nodes / 18,279 edges / 0 failures) from the new home.
4. **Fold in the source side.** Tystofte's `nb_A_build_metadata` (catalog extraction) and
   `nb_C_profile_timestamps` (profiling) become MetaAtomic's source-system reader, extending the
   graph upstream past `ingestion_boundary.py`. Extend `Node`/`Edge` per the field inventory in
   `docs/capability-map.md`.
5. **Element Logic source work.** Give the Element Logic graph its upstream source-system layer —
   billable, lands in MetaAtomic.
6. **Carl Ras portability gate.** Run against a second Atomic installation. The reusability claim is
   not accepted until this passes with no engine changes.

**Trigger — make "setup completed" observable.** Suggested line: the online enrichment run
(`NB_Lineage_Online.py`) is done and the viewer is published — i.e. LineageDocumentation
`CONTEXT.md` Next Actions 1-3 closed. Its Next Action 4 (semantic-model business-language metadata
distillation) is a *new phase writing new engine code*; that one belongs after the move, written in
MetaAtomic, not built in LineageDocumentation and migrated afterwards.

Step 3's reproduction of the Element Logic run (19,996 / 18,279 / 0 failures) is the move's pass/fail
and the safety net for doing it mid-engagement.

## Progress

**Now (2026-09-16):** the consolidation itself is done — the engine moved into `own/MetaAtomic`
(subtree, history kept, 08-04), Element Logic imports it and reproduces, the Carl Ras portability gate
passed with zero engine changes, and MetaAtomic has since become the product (ADR 0009) with four
packages and live deployments at Carl Ras (daily since 09-09) and Element Logic (pack awaiting Lars,
09-16). Of the task's sequence, step 4 (Tystofte source side) is not started and step 1's Element Logic
`git rm` of `lineage_engine/` is staged, not committed. Import mechanism still the interim `.pth`.

**Tried and dropped:** copying the engine -> `git subtree` (kept the history); the retired `meta.*`
island (`framework/`, `adapters/`) deleted 09-09 rather than migrated.

**Next:**
1. Decide whether this task closes as delivered (the consolidation) with the Tystofte source side
   and the import mechanism as new tasks, or stays open for them.
2. Commit the staged Element Logic `git rm` (customer repo, owner commits).
3. Fold in the Tystofte source side (`nb_A_build_metadata`, `nb_C_profile_timestamps`) and extend
   `Node`/`Edge` per `docs/capability-map.md`.
4. Give MetaAtomic its own `.venv` and settle the import mechanism.

## Needs from customer

- none (internal project)

## Why

Three projects each hold a piece: MetaAtomic has the name and the concept but no working code,
LineageDocumentation has the engine and UI but no source-system knowledge, Tystofte has source
extraction and profiling but no engine or UI. Without a physical consolidation the engine keeps
deepening inside a customer folder and MetaAtomic stays a shell.

Step 2 is time-sensitive: every LineageDocumentation session makes the move more expensive.

## Context

- ADR `own/MetaAtomic/docs/decisions/0009-metaatomic-is-the-product.md` (the decision)
- ADR `own/MetaAtomic/docs/decisions/0008-lineage-engine-as-shared-core.md` (model choice; partially superseded)
- `own/MetaAtomic/docs/capability-map.md` (capability ownership + field-level schema reconciliation)
- `customers/ElementLogic/LineageDocumentation/CONTEXT.md`, `INBOX.md`
- `customers/Tystofte/Tystofte-Fabric/` — `nb_A_build_metadata`, `nb_C_profile_timestamps`
- `customers/Carl-Ras/CONTEXT.md` — the portability target

Open: `own` and `customers/ElementLogic` are separate local git repos, so the move loses history
unless deliberately preserved. Undecided whether deployments import via path, submodule or package.

## Log
- 2026-08-03 — created
- 2026-08-04 - v1 delivered to Element Logic and tagged `v1-elementlogic`. Steps 2-3 DONE: engine moved via subtree (history preserved), EL re-pointed via a `.pth`, run reproduces exactly (23,396 / 22,453 / 531). Step 6 DONE EARLY and PASSED: Carl Ras `Fabric-ETL` parsed with zero engine changes (7,687 / 6,650 / 122, 0 DDL failures), one edge set hand-verified against raw SQL. Step 1 partially open: the EL `git rm` is staged, not committed (customer repo). Step 4 (Tystofte source side) not started.
- 2026-08-05 - Carl Ras semantic model added by owner and run. Auto-discovery misses a nested `*.SemanticModel` (cli.py:66-67 searches root/parent/grandparent only) - use `--semantic-model`. Engine defect found and fixed: `_database_name` read only the shared `DatabaseName` expression, so Carl Ras's inlined `Sql.Database(...)` partitions left the semantic layer unbound (source `?`, 0/0). Now bound 27 tables / 715 columns, edges 7,106 -> 7,848; EL re-verified with no regression. Carl Ras output persists at `customers/Carl-Ras/datahub/out/lineage/`.
- 2026-09-16 — brought onto the Progress shape (Progress + Needs from customer, fno_task none, customer_ask none); no facts changed. Card: CONTEXT.md converted to the resume card.
