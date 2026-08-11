---
id: skills-fabric-deployment-late-trigger
ts: 2026-08-11T18:30:00Z
type: evaluative
scope: client:Carl-Ras
source: /log
tags: [skills, fabric, deployment, evaluation]
status: distilled
description: "fabric-deployment and fabric-pipeline-notebook both failed to fire across a full day of exactly the work they describe; both were only consulted when explicitly invoked at the end"
---

Two skills covered this session's work precisely and neither fired on its own.

**`fabric-pipeline-notebook`** — its description names "notebook behaviour that differs
between interactive and pipeline-triggered runs". That *is* the session's central problem:
sempy calls that succeed interactively and 403 under a pipeline-triggered run. The whole
diagnosis was rebuilt from first principles (token claim decoding, endpoint-by-endpoint
probing) over several hours. It never fired.

**`fabric-deployment`** — its trigger list includes "deploy to TEST" and "the deployment
succeeded but it doesn't work in TEST". The session spent hours on deployment mechanics,
built `fabric_release.py`, and hit three of the skill's catalogued failure modes (stale
seeded table, per-environment value sets, identity not carried). It only fired when
invoked by name, near the end — at which point it contributed one thing the session had
*not* considered: the `DmsImportDatabaseException` ordering constraint on warehouse views
with three-part names, which was then pre-flighted and cleared.

Two observations worth acting on:

1. **The skills were right and useful — the cost was purely that they arrived late.** The
   independently-derived procedure matched the skill's four-step release almost exactly,
   which is corroboration, but it was paid for twice.
2. **Invoking a skill after the work is done still pays**, because it surfaces the failure
   modes not yet encountered. Consulting `fabric-deployment` *before* the first deployment
   of the day would have been cheaper than after.

Worth checking whether these descriptions are being matched at all for long sessions where
the triggering context appears mid-session rather than in the opening request.
