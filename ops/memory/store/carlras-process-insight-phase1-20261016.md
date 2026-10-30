---
id: carlras-process-insight-phase1-20261016
ts: 2026-10-16T12:00:00Z
type: semantic
scope: project:customers/Carl-Ras/process-insight
source: /log session a007db1c
tags: [carl-ras, process-insight, ontology, dax, dataverse, phase-1]
status: distilled
description: "process-insight phase 1 done 2026-10-16: spec + onboarding (155 metrics), metric-to-DAX (162 defined, all run on a synthetic model), config/overlay + deploy_check; test source copied into Pingala NielsWorkspace_Dev; phase 2 next"
---

- Product code in `own/ProcessInsight` (commit `fdec8b0`, AAI `3206abc`): `tools/onboard.py`
  (procedure `docs/05-library-onboarding.md`), `tools/measures.py` (DAX), `tools/testmodel.py`
  (live check on a synthetic Direct Lake model in leita.dk), `tools/deploy_check.py`
  (config + overlay -> `spec.lock.yaml`), `tools/testsource_copy.py`.
- Model rules decided: P3 revised (simple model first, measures second; one Calendar, inactive
  relationships + USERELATIONSHIP, no TREATAS, SQLBI 108 ms vs 7,464 ms); SQLBI rules A/B/C.
- Test source in Pingala `NielsWorkspace_Dev`: `Lakehouse_Landingzone_DataverseService` (778
  tables, 17 cases), `...DataverseSales` (744), metadata in `Files/metadata/`. The 10
  change-tracked tables were not yet in OneLake on 2026-10-16; rerun the copy before 2026-11-14.
- Next: phase 2 (metadata reader, Raw SCD2 + Enriched generator); test-data decision before phase 4.
