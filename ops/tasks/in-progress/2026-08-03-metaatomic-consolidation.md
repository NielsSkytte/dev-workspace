---
title: Consolidate lineage engine + Tystofte source extraction into MetaAtomic
status: in-progress
created: 2026-08-03
project: own/MetaAtomic
owner: architect
priority: high
blocked_by: (unblocked 2026-08-04 — v1 delivered; steps 0-3 and 6 done, step 1 commit awaiting owner)
activity:
fno_task:
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
