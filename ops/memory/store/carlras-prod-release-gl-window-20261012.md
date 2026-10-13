---
id: carlras-prod-release-gl-window-20261012
ts: 2026-10-12T20:00:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: /log
tags: [carl-ras, fabric, prod, release, general-ledger, variable-library, data-quality]
status: distilled
description: "Carl Ras 2026-10-12: GL curated window set to 3 years and released DEV->TEST->PROD; a release switches VL active value sets, so Prod placeholder sets break PROD ingest; only the RecId 5638443880 overflow still fails PL_MainExecution"
---

- Git held `fact.GeneralLedgerTransactions` as current-month-only; DEV looked wider only because a
  hand data load widened it and the nightly rebuild shrank it back. Fixed to 3 years (`Fabric-ETL`
  99f6814). DEV, TEST, PROD all 23.4M rows from 2023-10-01.
- `fabric_release.py` switches each library's active value set to the stage's set. PROD's
  `VL_PingalaUtils` Prod set held `[insert for prod]`, which would have broken the two Raw ingest
  notebooks; fixed by making it equal to Default. Check a Prod set for placeholders before a release.
- `fabric_release.py --exclude NAME` leaves one item out of a selective deploy (used for the TEST-only
  `CIData` lakehouse).
- PROD `PL_MainExecution` 10-12: all steps green except the semantic-model refresh (Currency overflow,
  one AX09 row). Scale Up passed after failing 10-10/11, cause unknown.
- Design consequence: a bad row must be tagged and moved to a fix area without stopping the flow;
  instruction at `own/MetaAtomic/docs/dq-quarantine-instruction.md` (reverses the 09-18 reporting-only
  narrowing; ADR 0018 first).
