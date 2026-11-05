---
title: Carl Ras — process-insight v1 (Dataverse → ontology → Direct Lake models + coverage report, three metric libraries)
status: in-progress
created: 2026-10-13
project: customers/Carl-Ras/process-insight
owner: architect
priority: normal
blocked_by:
activity:
fno_task: none        # Case to Resolution part: CarlRData-740 (230-02, activity 112930), owner 2026-10-31; rest Proj ID not agreed
customer_ask: none
waiting_on:
resume_on:
source: direct
---

## What
Build v1 of process-insight at Carl Ras as agreed in `customers/Carl-Ras/process-insight/CONTEXT_DECISIONS.md`
(D1–D12, P1–P7). Done when: on DEV, one Pingala-side command builds everything for the Case to
Resolution, Sales and Customer Insight libraries, and every metric shows one of the seven coverage
states with evidence; TEST/PROD run the same command per stage.

## Why
Process first: Carl Ras gets the full picture of its business in numbers from day one, and the
coverage report says what to fix next. It is also the Ontology accelerator's Dataverse slice.

## Progress
**Now (2026-11-05, Simon's work integrated):** Niels chose key rule (a) (to revisit: two key forms) and gave the go for integration steps 1-4. The order of work stays process first. Simon is away until January, so nothing waits for him. Commits on the engine branch:
- 84d2ea3 / aa000e4: decisions recorded.
- 2e7e949 / f6b8770: `key_form: dataarea_recid` keys `<DataAreaId>-<RecId>` as varchar. `spec/bindings/ax2009.yaml` binds the ITD entities over the Carl Ras AX09 Enriched views (0 errors against the Fabric-ETL DDL).
- 3466847: the AX 2009 catalog gets joins, anomalies and domains from AtomicInstructionSets@63d6d2a. The Carl Ras `source_values` are in `overlay.yaml`, uncommitted (customer repo).
- efd3235: `tools/enriched_lint.py` (S01-S26). `fo_enriched` writes no header.
- 3dc7e8a: the star is in house shape:
  - `pi_viewdimtransform` / `pi_viewfacttransform` plus the dim and fact procedures; on the install path, Lookup→ForEach pipelines.
  - PascalCase columns, info fields, an Orphan row in every dimension, foreign keys ISNULL to -1.
  - Curated reads the Enriched `<Table>_History` views, not Raw.
- 36c5234: dev redeploy with the house star.
  - ITD on NielsWorkspace: 204 measures, same totals except M60-046 (0 to blank) and 2 ageing measures that move with the date. M60-032 is still an error (AtomicBase duplicates).
  - C2R on NielsWorkspace_Dev: 0 Curated errors. 8 measures differ (M20-052/065/074/086/088/108/123): a foreign key that was NULL is now -1, so `<> -1` no longer counts empty keys as present.
  - Not yet: the Atomic Vision copies (PRs 942/943) and the coverage rerun.
- Fixed a side effect of 26df868 (model.py): a "none" dimension that a measure names stays in the model.
**Before (2026-11-03):** Engine work for Carl Ras C2R on own branch `processinsight/carlras-c2r-engine` (commits 4b4f5be, daafa27, 8d6b98c, b9c4004, ea13fae). After Mads's model review, every model is now a star extracted from the ontology (brief D38, D39): pass 5 of curated.py (tools/star.py) writes `pi_dim.Dim<Plural>` / `pi_fact.Fact<Plural>`, keys `SurrogateKey` / `SurrogateKey_<Dim>[_<Role>]`, fact → dimension relationships only, one level of parent attributes flattened into each dimension; `pi_curated` stays the graph. CTR on NielsWorkspace_Dev: star deployed, all 175 measures return the same totals as before. ITD on NielsWorkspace (2026-11-04): model `Inventory to deliver (star)` beside the restored pre-star `Inventory to deliver`; 204 measures with the same totals (5 differ in float rounding only), coverage states identical (record `deployments/nielsworkspace-fo/run.star.md`, `run.before-star.md`, `coverage-star/`). M60-032 errors in both (AtomicBase duplicate items, already open). Coverage model not republished from the star run. `Inventory to deliver (star)` also in Atomic Vision - Dev (PR 942 merged 2026-11-04, Update from git, same 204 totals); `Case to Resolution (star)` too (PR 943, same 175 totals as NielsWorkspace_Dev). Placement/config for Carl Ras must now list `pi_dim` and `pi_fact` as own schemas.
**Before (2026-10-28):** Inventory to deliver (ITD) runs in NielsWorkspace (48deed5a) from `tools/atomic_install.py`, which now also has snapshot, models and coverage steps, Util from AtomicBase notebooks when no reference platform, model names from the library title (own/ProcessInsight eb4db16). ITD coverage of 194: Working 50, Empty 7, ETL gap 9, Not landed 69, Other source not ingested 27, No data 32. Case to Resolution (CTR) redeployed in NielsWorkspace_Dev (pi_ schemas, compat 1708): Working 16, Empty 35, ETL gap 23, Not landed 52, not ingested 21, No data 8.
Atomic Vision - Dev (4e7cb5f8, repo pingalaglobal/atomicvision, main) holds both models and Process Insight Coverage (one run, both libraries, 349 metrics, Atomic Vision theme, State slicer on Metric detail), merged as PRs 913-916; Direct Lake on OneLake reads the data in NielsWorkspace / NielsWorkspace_Dev. Engine: ETL gap split into ETL gap / Not landed (brief D36, own 931fa72); onboarding needs a live snapshot (e9a0edc); architecture `own/ProcessInsight/docs/09-architecture.md`, client page `docs/pitch/process-insight-engine.html` (f03ba54).
Full installer rerun 2026-10-28: snapshot step proven (415 landed tables, 2 h); all default steps completed after a token-renewal fix; coverage unchanged.
**Tried and dropped:** TREATAS for role filters (SQLBI: USERELATIONSHIP far faster); a new workspace `Ontology-Test-LZ` (Niels: use `NielsWorkspace_Dev`); `CDCreader` for the Raw read (source tables have no change feed; watermark read instead). Option A for Atomic Vision (own data chain there): Niels chose B, the data stays in NielsWorkspace. `COL_LENGTH` in warehouse DDL: not supported by Fabric Warehouse; INFORMATION_SCHEMA instead.
**Next:**
1. Niels decides: M20-065 / M20-108 give BLANK where the foreign key has no source (recommended), then redeploy C2R on NielsWorkspace_Dev.
2. Atomic Vision PR with both house-shaped star models (replaces the PR 942/943 copies); merge only on Niels's go.
3. Niels commits `customers/Carl-Ras/process-insight/overlay.yaml` (AX09 `source_values`).
4. Rerun coverage for ITD and C2R on the house star; drop the stale star views in `pi_curated_view`.
5. Revisit two key forms (hash vs `DataAreaId-RecId`), noted in 03-spec-schema 3.2.
6. Remaining deploy gaps (review 2026-10-28): coverage as the last step of PL_PI_Main in Fabric; a models-only deploy tool for git workspaces (the Atomic Vision deploy was manual: clone, copy, PR, sync, refresh); the git path end to end with an F&O extension; an ITD golden test.
7. F&O enum notebook (`util.enums`) untested with real credentials: needs a client Key Vault and an SPN that reads F&O.
8. Regenerate `Case to Resolution Synthetic` and `ITD_Synthetic_Model` at 1708; drop the old cold/enriched schemas in NielsWorkspace_Dev; decide the PL_PI_Main schedule.
9. Niels sends `note-atomicbase-jesper-lars.md` (deferred 2026-10-28).
10. ITD review gaps: a daily on-hand snapshot in Curated; the synthetic input gives no column meanings.
11. R5: exclude parent-propagated child resolutions from M20-001/002/104 (measure change).
12. When the author returns a new library export: re-import, apply accepted L-changes.
13. ServiceNow 6b: wake PDI dev443926 (Niels), then check login and land metadata.
14. Sales and Customer Insight libraries through `05-library-onboarding.md` when exported.
15. Later: spike 0g (graph directly on Warehouse).

## Needs from customer
- New Proj ID for this work — not sent.

## Context
- `own/ProcessInsight/docs/01-product-plan.md` — product plan and build phases
- `customers/Carl-Ras/process-insight/design/PLAN.md` — Carl Ras configuration and deployment
- `customers/Carl-Ras/process-insight/CONTEXT.md`, `CONTEXT_DECISIONS.md`, `input/`
- `own/ProcessInsight/docs/00-project-brief.md` (D26-D32, section 3h)
- `own/MetaAtomic/CONTEXT.md` — lineage and verification capabilities this needs

## Log
- 2026-10-13 — created
- 2026-10-15 — started (session task)
- 2026-10-15 — plan split: product half to own/ProcessInsight/docs/01-product-plan.md (own 2446dd7, AAI e03f529); existing-source binding decided (D13 / brief D32)
- 2026-10-16 — phase 1 closed (config/overlay schema, deploy_check.py, Carl Ras config); test source copied into Pingala NielsWorkspace_Dev (Service 778, Sales 744 tables + metadata snapshot)
- 2026-10-18 — phase 3 done (binding corrections, stored.yaml, 66 of 175 measures valued); R1-R5 decided; library change request sent
- 2026-10-25 — Atomic installer built; core Atomic F&O + ITD extension installed in NielsWorkspace (run 1); run 2 interrupted by restart
- 2026-10-28 — ETL gap split (D36); ITD + CTR models and one coverage model in Atomic Vision - Dev (PRs 913-916); installer gets snapshot/models/coverage steps; architecture doc and client page
- 2026-11-05 — Simon's AtomicInstructionSets integrated (steps 1-4): AX09 key form + binding, AX09 catalog, enriched lint, house-shaped star; dev redeploy ITD + C2R (own 84d2ea3..36c5234)
