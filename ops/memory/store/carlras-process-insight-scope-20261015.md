---
id: carlras-process-insight-scope-20261015
ts: 2026-10-15T12:00:00Z
type: semantic
scope: project:customers/Carl-Ras/process-insight
source: /log
tags: [carl-ras, process-insight, ontology, aai, dataverse, servicenow, product]
status: distilled
description: "process-insight is the Ontology accelerator's Dataverse slice (product = own/Ontology, Carl Ras = first deployment); product plan in own/Ontology/docs/01-product-plan.md, Carl Ras half in process-insight/design/PLAN.md; nothing built"
---

- Ontology (AAI, `own/Ontology`) is the product; process-insight is its Dataverse slice and
  Carl Ras its first deployment. MetaAtomic stays a separate product (lineage + evidence).
- Product plan: `own/Ontology/docs/01-product-plan.md` (anonymised, synced to AAI main). Carl Ras
  configuration, deployment and session record: `customers/Carl-Ras/process-insight/design/PLAN.md`
  (customer repo, uncommitted). Decisions: process-insight `CONTEXT_DECISIONS.md` D1-D13, P1-P7;
  brief D26-D32.
- Key choices: every metric ships as a measure from day one; seven coverage states; AI stops at
  the YAML spec, deterministic projection after; one ontology spanning all libraries, one Direct
  Lake model per library; ServiceNow adapter from Aeven AtomicServiceNow (D30); existing-source
  binding is a product capability (D32).
- Carl Ras Dataverse has no customer service data yet (arrives later); AtomicBase has none either.
- Next: phase 1a library-to-source concept mapping (104 "data needed" phrases → concepts).
