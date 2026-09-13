---
id: metaatomic-join-provenance-and-sqlglot-scopes
ts: 2026-09-13T20:50:00Z
type: semantic
scope: own/MetaAtomic
source: session:0f971801
tags: [lineage, sqlglot, tsql, carl-ras]
status: distilled
description: "MetaAtomic 0.5.0: a join is recorded as written even when a side is a CTE (most Atomic joins are), the whole composite ON is carried, and the scope lookup keys on joined aliases because sqlglot hands each lineage scope back detached from its CTE parent"
---

Three things settled while making a join-product column say which joins produced it
(`own/metaatomic` `9f51ccc`).

**Most joins in an Atomic transform view are CTE-to-CTE.** The engine had recorded a join only
when BOTH sides resolved to physical tables, which is the condition for emitting a column-grain
`join-key` edge. Measured on Carl Ras `Fabric-ETL`: `viewoutboundtransform.Marketo_Lead` joins
four CTEs in its outer scope and lost all four. So a join is now recorded **as written**,
whatever its sides are; only the physical-to-physical pairs become edges, and a CTE join is never
invented into one because there is no column node to point at. Column edges carrying an ON went
47 -> 1,509 across the repo, and 2,880 view columns gained join context from 0.

**A composite ON must be carried whole.** The predicate had been stored per equality and keyed by
the joined alias, so the last equality overwrote the rest: `SalesOrder` reported
`PIN_DataAreaId` alone and `SalesId` was gone. Half of a composite key shown as the whole key
misleads a reader more than showing nothing.

**sqlglot's lineage tree hands each scope back detached from its CTE parent.** Walking
`Node.source` gives the qualified `exp.Select` of the scope a column was read in, with its joins
intact - but `select.parent` is no longer the `exp.CTE`, so the CTE name is gone and cannot key a
lookup back to the joins parsed off the original tree. The joined aliases survive `qualify`
(lowercased) and are what the scope is being looked up FOR, so the key is the frozenset of
joined aliases. sqlglot's own `walk()` also drops the parent link, and the parent is what says
which scope a leaf was reached through, so the engine walks the tree itself.

**Wording, and why it matters.** The viewer says "read under N joins", not "built from". The
joins of a scope state the ROW SET the value was read under; a LEFT JOIN whose columns the value
never reads did not change the value. Claiming otherwise would be the kind of implication the
fact-only rule forbids.
