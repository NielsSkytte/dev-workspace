---
id: datacompare-entities-vs-facts
ts: 2026-09-09T08:40:00Z
type: semantic
scope: project:customers/Matas/DataCompare
tags: [project, matas, datacompare, architecture, entity, dimension, fact, purchase-order, matching]
source: /log
status: distilled
description: "DataCompare compares dimensions: one row per party per legal entity, field by field, equality semantics, value-pair acceptance rules. The code is keyed for more of them (FIELDS per entity, ADAPTERS per (system type, entity), shared party CTEs) so Customer is an adapter plus a field list plus a pair row. Comparing PO/SO/TO is a different job - document+line grain, far higher volume, documents whose state changes hourly, and reconciliation with tolerance rather than value equality - and the two places that assume a dimension are the API vendors payload naming and dc.matched/dc.missing carrying account, name and on-hold columns"
---

**What generalised cleanly and what did not.** The database was entity-keyed from the start
(`dc.compare_pair.entity`, `dc.run.entity`, `dc.field_meta` per entity), so adding an entity needs no
migration. The Python was not: one module-level `FIELDS` list and `ADAPTERS` keyed on system type
alone. Both were fixed on 2026-09-09 and verified by re-running the vendor compare to identical
output.

**The rule that keeps being learned.** Vendors match on (mapped legal entity, account number) only
because a probe proved 11,264 of 11,290 MFO accounts exist in GFO. Every new entity needs its own
evidence before a match method is chosen; assuming the key survives is how a comparison quietly
reports garbage.

**Label tables are not entities.** PaymTerm and PaymMode carry the words behind a code. MFO's are
Danish, GFO's English, so comparing the labels reports a translation as a data error on nearly every
row. Join them for context; if the difference must be a finding, it belongs in a transformation map
that normalises language.

**Why facts are a different engine, not a bigger field list.** A dimension row is stable and keyed by
account; an order line is keyed by document + line, changes state through the day, and arrives in
volumes that rule out an in-memory full-field compare. The useful answer for a fact is usually count
and sum per legal entity and period, with tolerance rules (amount within x, date within n days),
rather than the value-pair equality that `dc.finding` and `dc.accept_rule` assume. The pair model, the
run history and the rules lifecycle all survive that; what has to give is the record key
(`dc.matched`/`dc.missing` carry account, name and on-hold today) and the finding kind.
