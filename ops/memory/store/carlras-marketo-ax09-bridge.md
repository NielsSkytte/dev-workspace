---
id: carlras-marketo-ax09-bridge
ts: 2026-08-11T00:00:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: session:5bbffdc6-903f-456e-9d01-a37807792a96
tags: [project, marketo, ax09, identity, modelling]
status: distilled
description: "Marketo->AX09 identity: email resolves 87% to a debitor via contactperson; the 16% ambiguity is real people on several customers, so the bridge must stay many-to-many"
---

Closes ingest decision 3.6, deferred since 2026-08-07 until Raw held data. Measured on
`Lakehouse_Raw_Marketo.leads` (31,217 current rows / 30,653 distinct emails) against
`Lakehouse_Raw_AX09`, current SCD rows only, exact trimmed-lowercased match. Reproducible:
`customers/Carl-Ras/datahub/tools/ax09_marketo_match.py`.

**The bridge works: 87.0% of Marketo persons resolve to an AX09 debitor.** `contactperson.EMAIL`
matches 88.8%, and 97.7% of those rows carry a `CUSTACCOUNT`. 92.5% among persons with
`accountName` populated. `custtable.EMAIL` matches only 12.4% and is *not* the bridge — it holds
the company's address, not the person's.

**This corrects the standing conclusion in [[carlras-marketo-source-findings]].** That record said
no ERP key is populated on the Marketo person, which is still true, and treated it as possibly
fatal, which was wrong. **The key does not have to be on the source system** — AX09 already holds
the email→debitor mapping itself. Generalises: before concluding a join is impossible, check
whether the *other* side already carries the mapping.

**An earlier pass on the same join read 54.8%** and was not wrong, just differently scoped: its
denominator was 995 rows from `createdAt`-filtered research extracts, i.e. recent signups, which
skew to private consumer addresses (gmail/hotmail were 47% of misses) that a builders' merchant
does not hold as contacts. Population beats sample; a recency-filtered extract is not a sample of
the base.

**The 15.9% ambiguity (4,333 of 27,234) is real, not dirty data.** 83.8% of ambiguous emails map to
exactly 2 debitors, but only 29.6% of those share one customer name; among the 93 emails with ≥5
debitors, exactly 1 does, and the maximum fan-out is 286. High fan-out local-parts are personal
names, not `info@`. No case crosses a `DATAAREAID`. So the dominant case is one real person
registered as contact on several distinct customers — a purchasing manager, administrator or agent.

**Consequence for the model:** do not collapse to a winner debitor; it would be wrong for 73% of
ambiguous cases. The bridge is one row per (email, debitor), genuinely many-to-many, with a
fan-out count on the row so reports can exclude extremes deliberately. Double-counting is handled
in the model — engagement is additive at *person* grain — not by flattening the view.

**Blocker found in passing:** `Lakehouse_Raw_AX09`'s SQL endpoint cannot serve data.
`INFORMATION_SCHEMA` queries work; any data query fails with `Retrieval of MWC token used for
accessing storage failed … Have the warehouse owner log in again`. Stale owner credential on the
Fabric item. Worked around by reading Delta directly from OneLake with an `az` storage token — the
same pure-Python route the GTM ingest uses. Not fixed; it will hit anything querying AX09 over SQL.

Two SQL-endpoint gotchas worth keeping: the endpoint's collation is **case-sensitive**, so
`LIKE '%mail%'` finds nothing against AX09's uppercase column names; and `SCDcurrent` is a
**string** (`"true"`/`"false"`), not a boolean.
