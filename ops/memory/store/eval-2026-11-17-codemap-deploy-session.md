---
id: eval-2026-11-17-codemap-deploy-session
ts: 2026-11-17T22:00:00Z
type: evaluative
scope: project:customers/Aeven/AtomicServiceNow
source: session cf6eaca2
tags: [evaluative, skill, fabric-warehouse-git, quiet-transcript]
status: distilled
description: "evaluative: fabric-warehouse-git lacked the manual-refresh rule and the no-warehouse-deploy rule (added #7, #8); assistant proposed deploying Warehouse_Curated against the runbook, Niels caught it; quiet-transcript fold links unusable in Orca (fixed)"
---

- `fabric-warehouse-git` did not say notebook DDL needs a manual Source control refresh; time was lost on "nothing to
  commit". Added as #7. It also lacked "a warehouse whose views a notebook generates is not deployed"; added as #8.
- The assistant suggested deploying `Warehouse_Curated` to PROD although `docs/production-deployment.md` says warehouses
  are never deployed; Niels challenged it ("are you 100 % sure"). Lesson: read the runbook before proposing a PROD route.
- quiet-transcript: fold links (`code.quiet-transcript.local`) cannot open in Orca, which catches link clicks; the mod now
  shows code in full when `TERM_PROGRAM=Orca` (`06a7961`).
