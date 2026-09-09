---
id: value-pair-key-collision-no-separator
ts: 2026-09-08T12:50:00Z
type: semantic
scope: project:customers/Matas/DataCompare
source: /log
tags: [project, matas, datacompare, defect, grouping, key, javascript]
status: distilled
description: "A grouping key built by joining parts with no separator collides: DataCompare grouped value pairs on field + legal-entity pair + both normalised values with an empty join, so a value plus blank and blank plus the same value produced one key - a blank-in-master finding merged with its mirror blank-in-compared finding into one row showing one pair's values with both counted. Found live on AddressZipCode kise>kise 2860, which claimed 2 vendors for a pair that has 1. Fixed by joining on a unit separator in app.js and report.py"
---

**Why it stayed invisible.** The row looked plausible - a real field, a real legal-entity pair, real
values - and only the count was wrong. It surfaced because a new drill-down filtered the vendor list to
the selected pair and the vendor count did not match the row's count.

**The consequence if it had shipped.** Accept on such a row creates a rule for the displayed pair only,
while the row claims to cover both, so the register would have documented a decision that did not match
what it did.
