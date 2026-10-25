---
title: Carl Ras — process-insight v1 (Dataverse → ontology → Direct Lake models + coverage report, three metric libraries)
status: in-progress
created: 2026-10-13
project: customers/Carl-Ras/process-insight
owner: architect
priority: normal
blocked_by:
activity:
fno_task: none        # new Proj ID not yet agreed with Carl Ras
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
**Now (2026-10-25):** Curated build is views + CTAS in four passes, no UPDATE (own/Ontology 6a2730f, decision row 2026-10-21, Niels approved four passes and no DuckDB in the build 2026-10-23). Phase 4 option A built (own/Ontology e484a2b): `tools/synthetic.py` + `tests/synthetic/case-to-resolution.yaml` (26 story cases, Sep 2026) through the real pipeline as source `DataverseSynthetic` in `NielsWorkspace_Dev`, model `Case to Resolution Synthetic`; 23 hand-checked values, 20 pass, sanity pass over all 175 measures clean. Fixed: medians/p90 counted blanks as 0 (both models redeployed; test source now 67 valued). The three definition fixes it found (SLA attainment, survey response rate, KB size) applied with Niels's go (own/Ontology f113dcf): 23 of 23 pass; test-source model now 69 valued, 0 errors. 2026-10-24 (own/Ontology c61d6b2, 9e33eb1): all measures on one `_Measures` table (`Measures` is reserved), display folders = library area\process, a rule for every new library (05-library-onboarding rule 4.5.13); M20-016 counts the published state at period end. Test-source model 70 valued, synthetic 23 of 23. Direct Lake (own/Ontology d09a9f1): automatic updates stay ON (CTAS deletes the framed files; datahub assessment 2026-08-19), `model.py frame` reframes with retry as the build's last step; plan text updated. Productising (Niels 2026-10-24: close the gaps, end goal = deploy to a customer by git push; next library = Inventory to deliver): golden regression test + 6 MB fixture (3521cee); onboarding runs unattended with review file (52077f8), holdout corrected 0633aad: 3 identical, 4 same DAX, 3 other DAX (M20-013 missed a filter at high confidence); intake design `docs/08-library-intake.md` (I1 source identification, I2 placement agreement; Niels: Inventory to deliver only after max genericity) awaiting Niels's yes; genericity A, B, D, E, H done (7de866b..363388e); git-deploy design `docs/07-git-deploy.md` (G0-G9); G1 emitter `tools/emit.py` (27c1ecf); Inventory to deliver research `docs/research/inventory-to-deliver-sources.md` (8b34149). Intake agreed by Niels 2026-10-24: I1 `tools/source_scan.py` (0395ec8), I2 `tools/placement.py` (06eb3ac; Carl Ras proposal: reuse AX09, new Dataverse Raw/Enriched, own schemas in Warehouse_Curated, 0 conflicts). G0: AAI branch `rehearsal/process-insight` folder `Rehearsal/ProcessInsight`, workspace `NielsWorkspace_GitRehearsal` c5f7c43c-7000-4d4b-95f8-763baed772d9 in leita.dk (Niels: leita.dk, not Pingala); `leitatesting` resumed + assigned (Niels's go 2026-10-24; pause at session end); git connect still NotConnected per API (existing GitHub connection GIT-skytte is for another repo, ConnectionMismatch) — waits on Niels; source catalogs ax2009/fo (01d2db8); existing-Atomic adapter `tools/warehouse_reader.py` + curated `kind: existing` (89db817; no derive, no labels, live checks pending); onboarding agent qualifier self-check, eval 2: 8 of 10 same DAX, 2 medium (af8e42f); create-or-bind `tools/fabric_platform.py` (fd129e9); git connection GIT-AAI made by Niels, workspace connected by the tool; rule 08 section 5 mixed sources + ownership (89bc24c) built: multi-source Curated incl. generated+existing, identity map, N-source cut-over (5a2efdc, d430798), pi_ schemas, owned.yaml; rehearsal G2-G7 done from git in leita.dk (Raw 31 tables 15341 rows; Enriched + Curated DDL = CTAS; PL_PI_Main end to end 426 s; frame with notebook token; model + ontology via git); warehouse steps in a generated notebook (NB_PI_Transform) instead of SP activity — awaits Niels; Inventory to deliver first look (d70c7d9): 194 metrics, data hints instead of phrases, 3 library-shape gaps proposed; G8 done (`tools/release.py`, Test workspace d5c7920f, deployment pipeline, model rebound, frame Completed in Test), G9 done (`tools/command.py` with adopt step: 0 changes after a run, no-change run makes no commit; push-hook files written, not enabled) (own d6cd4a0); library-shape gaps closed (55a3516..ce6f8b5); capacity leitatesting paused 2026-10-24 after the rehearsal; Inventory to deliver unattended onboarding run done in scratch copy (81 of 194 defined, 113 BLANK with reason, review file 615 rows / 38 low) — waits on Niels's review before take-over; tests made onboarding-independent; coverage states built (`tools/coverage.py`, own b18b386): Case to Resolution live on NielsWorkspace_Dev Working 13, Empty 35, ETL gap 78, Other source not ingested 21, No data 8; none-reason categories proposed in libraries/proposed/none-categories.yaml (waits on Niels); categories agreed (spec/bindings/none-categories.yaml) and grain check needs 3 months (66d3549): Working 15, Empty 35, ETL gap 76, not ingested 21, No data 8; coverage model + report deployed to NielsWorkspace_Dev ("Process Insight Coverage" model 048a478b, report 72c10bb1; tables pi_coverage in Warehouse_Curated_Dataverse; own 7bcf32b), measures match, report not yet opened/rendered; review step changed with Niels's go 2026-10-25 (own/Ontology e5e0a2b): one-page review by kind + full appendix, synthetic check written by a separate run without the definitions, provisional until proven (proof.yaml); Inventory to deliver taken over as provisional; curated-level synthetic check (ITD_Synthetic_Model in NielsWorkspace_Dev) 22 headline metrics, 20 pass/proven, 2 fail (M60-032 per item, M60-124 open quality orders) on the one-page review; check found and fixed: M60-095 counted return lines, no Calendar relationship for date-typed columns; open: synthetic input gives no column meanings (agent doubled on-hand value, fixed in the scenario); sanity flags M60-176 Freight variance (a negative variance, not a defect); Niels answered the one-page review yes to all 15 (own b51575f): M60-032 per item, M60-124 adds stock under open quality orders (on_quality_hold now stored), synthetic 22 of 22, ITD provisional 58 metrics, proven 23; inbox 2026-10-25 note read: NielsWorkspace_Dev folders reorganised by session ebd8d221 (items found by name, no impact), ITD I1 scan on Pingala Lakehouse_Raw_FO kept in own/Ontology deployments/pingala-fo (1096377); G3/G4 need it to settle whether table DDL goes into git.
Earlier (2026-10-19): phases 1-3 done on the test source (`NielsWorkspace_Dev`). Phase 3 (2026-10-18): binding corrected per research (own/Ontology 6d66c8f), Enriched 46 views, Curated 54 tables with `spec/stored.yaml` (54 of 66 stored columns computed, 12 none-with-reason, business minutes on the DK calendar), model `Case to Resolution` 175 measures / 0 errors / 66 with a value (blanks trace to empty trial tables or the data), ontology `Process_Insight`. R1-R5 approved 2026-10-18; library change request L1-L9 sent to the author 2026-10-18. leita.dk capacity paused 2026-10-17.
**Tried and dropped:** TREATAS for role filters (SQLBI: USERELATIONSHIP far faster); a new workspace `Ontology-Test-LZ` (Niels: use `NielsWorkspace_Dev`); `CDCreader` for the Raw read (source tables have no change feed; watermark read instead).
**Next:**
0. NEXT SESSION: run Inventory to deliver on the Pingala F&O base data (`Lakehouse_Raw_FO`, scan in own/Ontology `deployments/pingala-fo`; 78 of 194 metrics have their tables): F&O binding, Curated, model and coverage states in NielsWorkspace_Dev; recheck review rows 12/13 (fields and the 21 tables without a Learn page) against that metadata.
0b. Gap list from the ITD review: daily on-hand snapshot in Curated (row 1); synthetic input has no column meanings.
1. Phase 4 rest: coverage states with evidence per metric (MetaAtomic), then coverage model and report.
3. R5: exclude parent-propagated child resolutions from M20-001/002/104 (measure change).
4. When the author returns a new library export: re-import, apply accepted L-changes, adjust `stored.yaml`.
5. ServiceNow 6b: wake PDI dev443926 (Niels), then check login and land metadata.
6. Sales and Customer Insight libraries through `05-library-onboarding.md` when exported.
7. Later: spike 0g (graph directly on Warehouse).

## Needs from customer
- New Proj ID for this work — not sent.

## Context
- `own/Ontology/docs/01-product-plan.md` — product plan and build phases
- `customers/Carl-Ras/process-insight/design/PLAN.md` — Carl Ras configuration and deployment
- `customers/Carl-Ras/process-insight/CONTEXT.md`, `CONTEXT_DECISIONS.md`, `input/`
- `own/Ontology/docs/00-project-brief.md` (D26-D32, section 3h)
- `own/MetaAtomic/CONTEXT.md` — lineage and verification capabilities this needs

## Log
- 2026-10-13 — created
- 2026-10-15 — started (session task)
- 2026-10-15 — plan split: product half to own/Ontology/docs/01-product-plan.md (own 2446dd7, AAI e03f529); existing-source binding decided (D13 / brief D32)
- 2026-10-16 — phase 1 closed (config/overlay schema, deploy_check.py, Carl Ras config); test source copied into Pingala NielsWorkspace_Dev (Service 778, Sales 744 tables + metadata snapshot)
- 2026-10-18 — phase 3 done (binding corrections, stored.yaml, 66 of 175 measures valued); R1-R5 decided; library change request sent
