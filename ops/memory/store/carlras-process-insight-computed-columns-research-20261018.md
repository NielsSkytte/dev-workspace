---
id: carlras-process-insight-computed-columns-research-20261018
ts: 2026-10-18T12:35:00Z
type: semantic
scope: project:customers/Carl-Ras/process-insight
source: /log
tags: [process-insight, ontology, dataverse, servicenow, metric-library]
status: distilled
description: "Case to Resolution computed columns researched 2026-10-18 (own/Ontology 71a8ecb, 483ba89): of 57, 11 hold, 34 need a fix, 6 need a customer value, 6 have no Dataverse source (audit). Change request L1-L9 sent to the library author."
---

- Computed columns are ordinary Curated columns derived once per row (e.g. `is_duplicate`,
  `first_response_business_minutes`), not synthetic data. Research note:
  `own/Ontology/docs/06-dataverse-semantics.md` (sources under `docs/research/dataverse/`).
- Of 57: 11 hold as written, 34 need a fix (4 only partly computable), 6 need a customer-set value
  (e.g. mandatory stages, second-line queue), 6 have no source today (need audit; Link to Fabric does not export it).
- Industry/ServiceNow track: no common vendor FCR definition (industry adds no escalation, no callback);
  vendor "response" SLAs measure pickup, not a reply to the customer; SLA met is a breach flag once per
  case and target; one shared reopen window, default 7 days; escalation split specialist vs management.
- Change request (18 changes, 3 new metrics) sent to the library author 2026-10-18; our copy stays on
  the 13 Oct export until a new one arrives.
