---
id: datacompare-rule-kinds-and-match-keys
ts: 2026-10-09T12:30:00Z
type: semantic
scope: project:customers/Matas/DataCompare
source: /log
tags: [matas, datacompare, rules, match-keys, decision]
status: distilled
description: "DataCompare rules (2026-10-09): one judge rules.py for run and app; kinds value_pair, mapping, transform (plain remove-at-end/start, regex advanced), optional on-hold condition; Excel import = one mapping rule per field; match keys in compare.MATCH_KEYS recorded per run in dc.match_key; no rule is ever created automatically"
---

- **One judge:** `prototype/rules.py` judges every rule in the daily run and in the relay's in-place re-judge
  of the latest run. Plain value pairs still use the SQL `APPLY_RULE`; other kinds read the open findings,
  judge in Python and accept by id. A non-value-pair rule stores `<kind>` in value_a/value_b so an older
  notebook accepts nothing with it (an older notebook ignores `when`, so a conditional `*`/`*` value pair
  WOULD accept the whole field there - release notebook and rules together).
- **Kinds:** mapping `{map}`, transform `{ops, side}` with remove_end / remove_start / remove_text /
  strip_bracket_number as the plain options and regex under Advanced (owner: users cannot be expected to
  know regex), optional `when` on OnHoldStatus. Builder on the Rules register lists the field's open
  findings and previews per value pair. Schema: migrate_v4 (add-only), committed to `dev` ad966e8.
- **Match keys:** `compare.MATCH_KEYS[(type, entity)]` = table, legal-entity column, key columns
  (several joined with `|`); every load writes `dc.match_key`; the method card shows them. App editing
  waits for the config store.
- **Owner principle (2026-10-09):** no rule is generated automatically and nothing is AI-scored; the
  value-pair list is a deterministic grouping and the dominant-recode label accepts nothing.
- Design + slice 2: `prototype/DESIGN-custom-rules.md`.
