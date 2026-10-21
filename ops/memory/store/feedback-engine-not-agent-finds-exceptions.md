---
id: feedback-engine-not-agent-finds-exceptions
ts: 2026-10-21T23:45:00Z
type: feedback
scope: workspace
source: conversation
tags: [metaatomic, data-quality, rules, customer-data, agents]
status: distilled
description: "Niels 2026-10-21: an agent must never derive a customer rule or exception from reading their data (the 'group 989 may have no VAT number' case); finding such exceptions is the engine's job, generic and on every run"
---

- Niels's summary (2026-10-21): "analytics of actual data must always be engine; you can work on it to generate and
  build the engine, but it must never be you who creates the actual rule."
- Rule: an agent (Claude, a subagent) does not analyse a customer's data to author rules, exceptions or proposals for
  them. That is exactly what the engine must do, generically, on the daily run, with a person at the customer
  confirming before anything applies. The daily run cannot depend on an agent reading the data.
- Trigger: on 2026-10-21 an agent wrote the Carl Ras proposal "customer group 989 may have no VAT number" from run
  counts and an earlier finding (MD-03). Niels: "the 989 is not something you should ever do, but exactly something an
  engine should do." The handwritten draft was withdrawn; the engine now suggests exceptions (failure concentrated in
  one value of a low-cardinality column), live counts, confirm/reject by the customer.
- Refined by Niels the same evening: an agent MAY use a customer's data as an example to write GENERIC rules for a
  Pingala check set (e.g. AX09, F&O) - "use Carl Ras as an example to create the generic ax09 data quality pack". What
  an agent must never write is a rule specific to one customer (like 989 for Carl Ras), and it must not analyse data
  as a routine in production: that is the engine's daily job, with the customer confirming.
- So: generic check-set authoring from example data = agent, versioned and released like code; customer-specific rules
  and exceptions = engine suggestion + customer confirmation; reviewing engine output and building the engine = agent.
