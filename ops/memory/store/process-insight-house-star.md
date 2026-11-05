---
id: process-insight-house-star
type: fact
scope: project:customers/Carl-Ras/process-insight
date: 2026-11-04
status: distilled
---
Since own 3dc7e8a the process-insight star follows AtomicBase: views in `pi_viewdimtransform` / `pi_viewfacttransform` with a METADATA block, procedures sp_CreateDimTableAsSelect / sp_CreateFactTableAsSelect, Lookup -> ForEach pipelines PL_PI_Curated_Dim/Fact_UpdateData, PascalCase columns, Orphan row -1 in each dimension, FK ISNULL(-1). Curated reads Enriched `<View>_History` only. Consequence: DAX `<> -1` now treats empty FKs as missing (C2R: 8 measures changed 2026-11-04). Simon's work stays process-first; Simon is away until January.
