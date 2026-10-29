---
id: metaatomic-atomicbase-checksets-20261022
ts: 2026-10-22T15:50:00Z
type: semantic
scope: project:own/MetaAtomic
source: /log
tags: [metaatomic, atomicbase, check-sets, dq]
status: distilled
description: "MetaAtomic deployed into AtomicBase Fabric/00 - Services/MetaAtomic; Pingala check sets edited and versioned in MetaAtomic_Store dq.pack, released to JSON by pack release; customer overlay = diff + base version"
---

- MetaAtomic lives in AtomicBase ("Pingala Fabric Base", Azure DevOps, branch `Development`) under
  `Fabric/00 - Services/MetaAtomic` beside DataSentry and Pace: NB_MetaAtomic, NB_DataQuality, pipeline and
  `MetaAtomic_Store.SQLDatabase` in one folder (commit `f08e636`, 2026-10-22).
- Pingala check sets: working versions are rows in `dq.pack` in that store, each save a new version
  (1.1 -> 1.1.1 -> 1.1.2) with who/when/why. Released versions are JSON in `own/MetaAtomic`
  `dq_profile/packs/*.json`, copied there by `pack release`, shipped with the engine build.
- Customer version: a JSON overlay holding only the differences plus the Pingala version it was made on
  (Carl Ras copy in `Fabric-ETL/MetaAtomic/design/dq_packs/ax09.overlay.json`). Both are edited in the same editor.
- First DQ run in the Pingala Fabric base 2026-10-22: 686 tables, score 97.4. Active sets: ax09 1.1, fno 1.1,
  d365fo 2.0, atomic_curated 0.1. Saving a Pingala-version change from the deployed app was not yet tested.
- Niels wants the check set front and centre on the DQ page (which sets are in effect, which issues come from
  which set), issues above tables (own `671b7f1`, local preview).
