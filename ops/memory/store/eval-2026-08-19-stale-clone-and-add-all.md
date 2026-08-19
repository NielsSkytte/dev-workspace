---
id: eval-2026-08-19-stale-clone-and-add-all
type: evaluative
status: distilled
created: 2026-08-19
source: ops/memory/daily/2026-08-19.md
project: customers/Carl-Ras/datahub
---

# Two own-output failures with the same shape: trusting local state without checking it

**Stale clone.** Inventoried the Carl Ras semantic model - "one calculated column", "170 measures",
"37 tables" - from a `Semantic-Model` checkout last fetched 2026-08-01. Mads had pushed five commits
between 08-05 and 08-07. The blocker list was wrong as a result, and when the missing column surfaced
during an import failure I attributed it to "arrived this week" rather than "I never fetched". Niels
pushed back, and he was right. Corrected counts: two calculated columns, 3 calculation groups,
177 measures, 38 tables.

**`git add -A`.** Used it to stage a multi-file edit; it swept a concurrent session's uncommitted
`Campaign Forecasts.tmdl` fix into my commit and pushed it to the customer repo under an unrelated
message. Benign - it was Niels's own fix and he wanted it committed - but it bypassed the
customer-repo approval gate. Second occurrence in two days of one session's commit bundling
another's work (see `concurrent-session-commit-bundling`).

**Rules earned:** fetch before reading any repo you are about to reason from; stage by explicit path,
never `-A`, in a shared working tree.

**Skills:** ninth consecutive session with the Fabric skills silent. `fabric-warehouse-git` did not
fire on a hand-edited generated view going through git, and nothing owns Direct Lake conversion - the
whole assessment was built from MS Learn lookups. Candidate skill: Direct Lake conversion and its
failure modes (no calculated columns, no autobind on deployment, drop-create versus framing).
