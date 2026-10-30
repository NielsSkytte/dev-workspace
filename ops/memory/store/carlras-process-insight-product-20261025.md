---
id: carlras-process-insight-product-20261025
ts: 2026-10-25T12:00:00Z
type: semantic
scope: project:customers/Carl-Ras/process-insight
source: /log session eae86d9b
tags: [carl-ras, process-insight, ontology, git-deploy, onboarding, synthetic-check]
status: distilled
description: "process-insight 2026-10-24/25: product deployable by git push (G0-G9 rehearsed in leita.dk), intake I1/I2, mixed sources in pi_ schemas, coverage report; review step = one page + synthetic check + provisional until proven; Inventory to deliver onboarded, synthetic 22/22"
---

- own/ProcessInsight local commits through `b51575f` (not pushed). Goal (Niels 10-24): deploy to a customer
  with a git push; next library Inventory to deliver (F&O).
- Rules: one `_Measures` table (`Measures` is reserved), folders = library area\process; existing
  Atomic setup reused with own `pi_*` schemas, own `PL_PI_`/`NB_PI_` items, shared functions stay
  shared, `owned.yaml` records what we deploy.
- Rehearsal G0-G9 in leita.dk `NielsWorkspace_GitRehearsal` via AAI branch `rehearsal/process-insight`
  (git connection GIT-AAI made by Niels; gh OAuth token rejected as PAT). Capacity `leitatesting` paused.
- Review step (Niels 10-25): one-page review (max 15 headline decisions by kind), appendix
  `review-full.md`, synthetic check written by a separate agent run without the definitions
  (`onboard_agent.py --synthetic`), `proof.yaml` with definition fingerprint; C2R is `attended`.
- Curated-level synthetic check (`testmodel.py build --scenario`, `ITD_Synthetic_Model` in
  NielsWorkspace_Dev) found real defects: date-typed columns had no Calendar relationship (real
  generator too), M60-095 counted return lines. Gap: the synthetic input carries no column meanings
  (agent doubled F&O on-hand value = PostedValue + PhysicalValue).
- Next: run Inventory to deliver on Pingala `Lakehouse_Raw_FO` (78 of 194 metrics have their tables).
