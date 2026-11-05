---
id: carlras-prod-schedule-and-dq-mail
ts: 2026-11-05T18:30:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: /log
tags: [carl-ras, datahub, prod, schedule, dq-mail, metaatomic]
status: distilled
description: "Carl Ras PROD: first green PL_MainExecution 2026-11-03, schedule on weekdays 06:30 from 11-05; DQ mail works because PL_MetaAtomic runs as the last saver's account; pyz reaches stages from the main clone"
---

- First green PROD `PL_MainExecution`: 2026-11-03, 10:52-12:33 UTC. Schedule enabled 2026-11-04 (weekdays 06:30); DEV and TEST off.
- DQ mail: the Outlook connection cannot be shared, so the pipeline must run as Niels, the last person to save it. A deployment may require saving the connection again in that stage.
- `NB_MetaAtomic` and `PL_MetaAtomic` reached PROD 2026-11-04 through the "Fabric-ETL Deployment" pipeline, not by direct item writes.
- MetaAtomic release at a customer (owner): a deliberate push of a new pyz to `main`; every stage takes it at its next run.
