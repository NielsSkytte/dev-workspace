---
id: atomic-reference-docs
ts: 2026-10-05T12:00:00Z
type: semantic
scope: workspace
source: session:ee830441
tags: [atomic, pingala-fabric-platform, skill, reference]
status: distilled
description: "Pingala Atomic is described in two skill references: atomic-overview.md (what/why/components, no how-to) and atomic.md (implementation evidence per repo); Part 1 owner definition still open"
---

**Where (2026-10-05):** `C:\Dev\.claude\skills\pingala-fabric-platform\references\`
- `atomic-overview.md` -- what Atomic is, what it solves, its components and conventions, no
  procedures or paths. The file to hand another session or LLM.
- `atomic.md` -- Part 2 filled from the Element Logic repo snapshot
  (`customers/ElementLogic/LineageDocumentation/Input/Pingala Fabric ETL`) and the Carl Ras datahub
  repos; Part 1 owner definition still TODO.

**Facts found:** generic Atomic = AutoLoader ingestion (`NB_Ingest_*`, `pingalatool_spark`
CDCreader/SCDMerger, SCD2 on every Raw table), view -> CTAS procedures per schema triple, pipelines
that enumerate `INFORMATION_SCHEMA.VIEWS` (the views are the configuration), `PIN_*`/`SCD*` columns.
Off F&O (Carl Ras AX09): Pingala landing pipeline replaces the Dataverse link; Delta CDF on
overwritten LZ tables; Raw -> Curated unchanged. No customer-free Atomic repo and no view generator
found in either repo.

**Open (owner):** product vs method; canonical codebase; where the generator lives; whether
Particles/Atoms/Molecules is used beyond presentations. Owner will supply background material.
