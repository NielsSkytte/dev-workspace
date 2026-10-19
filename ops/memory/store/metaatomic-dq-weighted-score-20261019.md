---
id: metaatomic-dq-weighted-score-20261019
ts: 2026-10-19T09:00:00Z
type: semantic
scope: project:own/MetaAtomic
source: /log
tags: [metaatomic, data-quality, criticality, lineage, carl-ras]
status: distilled
description: "MetaAtomic DQ score: tables tiered by measure reach (own measures + join reach via view joins and model relationships); tier-weighted estate score 68.0 on Carl Ras DEV vs 76.5 mean over tables. Critical gate cap dropped by Niels 2026-10-19."
---

- Criticality: per table, own measures (built on its columns) and join reach (distinct measures across a
  joined table via view joins and semantic-model relationships). Carl Ras DEV lineage store (2026-10-18):
  raw->enriched 2,528 column edges, enriched->curated 881.
- Tier-weighted estate score 68.0 over 148 tables (tier 1 mean 59.3, tier 2 73.9, tier 3 74.1); the
  unweighted mean (76.5) hid that critical tables are the worst.
- The "critical gate" (cap at 60 if a tier-1 table is red) was proposed and **dropped by Niels 2026-10-19**.
- F (failing-row count at which a rule counts fully failed) is a row count, not a percentage: a percentage
  treats 2,062 bad rows in ~114M GL rows as nothing. F's value is a guess; best-practice research was requested.
- Delta-log row counts exist for every store (since 2026-09-16) but the DQ engine still counts through SQL,
  hence `42S02` on the two enriched reconcile checks (landing lakehouse in another workspace).
