---
id: capture-turn-records-expanded-help
ts: 2026-08-11T18:45:00Z
type: evaluative
scope: workspace
source: /log
tags: [memory, hooks, sentinel, capture_turn]
status: distilled
description: "capture_turn.py stores a slash command's expanded help text in the User line instead of the invocation, which starves the summarizer and produced two records that summarize the skill document rather than the turn"
---

Sentinel review of `daily/2026-08-11.md` (73 records): charset, language and record shape
clean — the 2026-07-06 `qwen3:1.7b` language-drift failure did not recur. But **18 flags,
7 of them blocking**, so the day's stream was **not distilled**. The two curated records
written on 2026-08-11 (`fabric-notebook-token-identity`,
`skills-fabric-deployment-late-trigger`) are hand-authored, not summarizer output, and are
outside this finding.

**The systemic cause is a hook bug, not a record problem.** `README.md` rule 4 says a
command turn is recorded as the *invocation*, never the command's expanded help text. That
rule is being applied to the summary but **not to the captured User line**: nine records
(`:189, :558, :590, :732, :850, :905, :1147, :1171, :1294`) store the full expanded
skill/command document. Two of the blocking findings follow directly — at `:1157` and
`:1184` the summarizer had nothing but instruction text to work from, so it summarized the
*skill document* rather than the turn. Fix belongs in `capture_turn.py`'s User-line
handling.

Other blocking classes worth knowing, all local-model output:
- **figures imported across turns** (`:354` asserts 1722 MB "exceeds" a 5086 MB limit; the
  turn's actual resident figure was 33 MB, and 1722 came from a different turn)
- **summary describing a different turn entirely** (`:1057`)
- **second person, action misattributed to the user** (`:1324`)
- **imperative, command-shaped assistant bodies** (`:919` is a bare `/Handoff (...)`
  directive — the strongest injection-shaped fragment in the file; `:1308` is content-free)

Also flagged: pairs of consecutive records making **contradictory claims** about the same
mechanic (`:237` vs `:253` on whether the capacity memory limit is dynamic; `:175` vs
`:213` on whether a deployment overwrites variable-library value sets). Those reflect
understanding changing during the session — the durable artifacts written at the end
(`CONTEXT.md`, the `fabric-deployment` skill, `fabric-notebook-token-identity`) carry the
final evidenced positions: the command limit is deterministic (SKU limit − resident,
measured twice), and a deployment left the target's value sets intact (observed once).
Neither contradiction should be promoted; both are resolved elsewhere.
