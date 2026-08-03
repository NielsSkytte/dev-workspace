---
id: datacompare-match-engine
ts: 2026-08-03T12:00:00Z
type: semantic
scope: project:customers/Matas/DataCompare
source: session:b6def628
tags: [project, matas, datacompare, entity-resolution, fabric, design]
status: distilled
description: "DataCompare Part 3 match engine: the three authority layers, why match_xref is sticky and ambiguous keys match nothing, and the equal-weight/leading-field-gate scoring forced by cfg.match_rule having no weights column"
---

Part 3 of DataCompare, built 2026-08-03 as `fabric/NB_Match_Engine.Notebook/` (Matas ADO repo
`GFOERPDataAnalysis`, commit `05f0313`). It decides which vendor party in a source system is the
same real-world vendor as one in the master, because the systems share no reliable identity key.
Input: the canonical layer's `canonical_record` + `canonical_value`. Config: `cfg.match_rule` +
`cfg.pinned_match`. Output: `match_xref` (accumulating) and `match_candidate` (review artifact).

**Three layers, in authority order** — pins, then deterministic rules in `rule_order`, then fuzzy.

**The four rules that make it safe, all decided in this build:**

1. **Ambiguity matches nothing.** A deterministic key value carried by more than one party on
   *either* side is skipped and counted, never resolved by picking one. Matching on a shared CVR
   number would silently pair the wrong legal entity.
2. **`match_xref` is sticky.** Once a source party is matched it keeps that master party on later
   runs even if the underlying key changes. A new deterministic hit that contradicts a standing row
   is reported, not applied. This is the whole point of "accumulating asset, not a run artifact":
   if identity churns day to day, the daily diff compares different vendors each night and means
   nothing.
3. **Only a pin repoints a party**, and fuzzy never auto-matches — proposals land in
   `match_candidate`, get reviewed, and return as `cfg.pinned_match` rows [D8].
4. **Scoring: equal weights, leading field as gate.** `cfg.match_rule.field_list` is a plain JSON
   array with no per-field weights (the seed row literally says "Initial weights TBD in Part 3").
   Rather than change the config schema on a guess, the score is the mean similarity over the rule
   fields *both* sides carry, gated on the first field (the name) clearing the threshold alone. A
   weighted variant needs a schema column — decide that against real data, not before.

**Bounding the fuzzy layer:** blocking on `AddressCountryRegionId` (a notebook parameter) — only
parties sharing that value are compared. Note the interaction: with country *in* the field list, a
cross-border pair cannot clear a 0.85 mean even when name and street match exactly (0.875 + 1.0 +
0.0)/3 = 0.625. Blocking and scoring both encode the country, which is deliberate for DK/SE/NO/FI
(see `nordic-vendor-entity-resolution`) but means the threshold is not comparable across rules with
different field counts.

**Verification without a lakehouse:** the match core is pure functions over frames, so a scratchpad
harness exec'd just those notebook cells (stubbing `notebookutils` and `deltalake`) and ran 30
checks — ambiguity both sides, composite keys, empty inputs, blocking/ranking/limit, every
accumulate path. This is the general trick for Fabric notebooks written before access exists: keep
I/O in its own cells and the logic testable from a plain venv.

**Still unverified against real data.** `NB_Probe_SourceLakehouses` is the gate: it measures whether
`TaxExemptNumber` is populated and unique enough to carry the only active deterministic rule, and
whether `VendorAccountNumber` survives MFO→GFO [D7], which would collapse most of the matching work.

**Workspace split (owner instruction, same day):** our items go in `GFO_DataCompare_dev`; the
Link-to-Fabric managed lakehouses stay untouched in `GFO_DataCompare` and are read cross-workspace
by `abfss://` path, so no copy of source data is made.
