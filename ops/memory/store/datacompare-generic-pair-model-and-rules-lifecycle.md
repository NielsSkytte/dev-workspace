---
id: datacompare-generic-pair-model-and-rules-lifecycle
ts: 2026-09-08T07:30:00Z
type: semantic
scope: project:customers/Matas/DataCompare
source: /log
tags: [project, matas, datacompare, fabric, sql-database, rules, lifecycle, onboarding, ax, nav, plain-language]
status: distilled
description: "DataCompare backend is pair-generic since 2026-09-07 evening (dc.compare_pair, A/B columns, PAIRS + ADAPTERS keyed by system type, live migration kept the run and the rules): AX or NAV = one adapter, one pair row, one legal-entity map. Rules are never deleted: retire reopens findings, reactivate re-applies, dc.rule_event keeps who/when/why per transition (the test flow after an F&O fix). A rules register page and two plain-language endpoints (method, rules) exist; the owner wants that text as flat manual lines, not prose"
---

**Why the generalisation happened before the Fabric port.** The owner asked how much rework AX and
NAV would need. Honest answer: the design was source-agnostic, the prototype named MFO/GFO in every
column. The fix cost a day and was done at once: `dc.compare_pair` (system_a, system_b, types,
match_method, master_default), `_a/_b` columns on finding, matched, code_map, accept_rule,
entity_map, run; `migrate_v2.py` converted the live database in place (42,989 findings, the active
rule and its 5,890 accepted findings, 36 entity-map rows, both runs all kept). `compare.py` has
`PAIRS` and `ADAPTERS = {"D365FO": build_flat_d365fo}`. README section "Onboarding a new source":
pull to `data/<code>/`, one adapter producing the canonical flat columns, one PAIRS entry with
company map and match method, `python load_sql.py`. Nothing else changes. The match engine
(Part 3 notebook) plugs into a pair whose `match_method` is `engine`.

**Rules lifecycle (owner requirement, scheduled runs in mind).** A rule is never deleted. Active
-> Retire (reason): its findings on the latest run reopen. Retired -> Reactivate (reason): status
active, findings re-accepted. Every transition is a `dc.rule_event` row (created | retired |
reactivated, actor, at, reason, run_id, findings_affected). The test flow after the F&O developers
say something is fixed: retire the rule, let the scheduled run show whether the findings return,
reactivate if they do. `app/rules.html` is the register: filters (status, field, pair, text), sort,
group-by-field, expandable rows with the plain sentence, the event history and the buttons. The
main page keeps Accept / Retire on value pairs and a summary card with the last five events.

**Plain-language layer.** `GET /api/method` renders the comparison logic as 14 labelled lines,
`GET /api/rules/plain` renders each rule as one entry ("Field: sales tax group. Legal entities:
maop -> modk. MFO value: DK_KOB. GFO value: DOM_AP. Created by ..., 7 Sep 2026. Reason: auto remap
of codes. Status: active. Findings covered in this run: 5,890."). Templates and label maps live in
the relay; every number comes from SQL. The first draft read as prose; the owner asked twice for
shorter, then for "boring instruction text". The register that stuck: one labelled statement per
line, no connective sentences, top three recodings per field with a count of the rest.
