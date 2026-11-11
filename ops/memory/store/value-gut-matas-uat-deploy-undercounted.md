---
id: value-gut-matas-uat-deploy-undercounted
ts: 2026-11-11T21:00:00Z
type: evaluative
scope: project:customers/Matas/DataCompare
tags: [time, value-model, adr-004, matas, deployment]
status: distilled
description: "Owner gut 2026-11-11: Matas DataCompare W46 weighted 6.25 h on 4.00 registered is far too low; deploying the full setup to UAT and finding production issues is not 1:1 work"
---

- Week 2026-W46 (11-09..11-11): Matas DataCompare Task-72114 registered 4.00 h, weighted 6.25 h (156%); 11-10 timesheet 2.25 h.
- Owner (2026-11-11): "matas needs to be way higher" - the whole setup was deployed to UAT (Static Web App, app registration,
  sign-in fix) and several issues for the production deploy were identified; that is not 1:1 with time spent.
- Disagreement direction: model too LOW.
- Inference: the value model weights file output (artifact/knowledge rows); deployment and diagnosis work runs as
  az/CLI commands against Matas's tenant and leaves few file rows, so it is under-weighted. Not verified.
- Evidence for the ADR-004 re-evaluation: deployment / environment work needs its own weight.
