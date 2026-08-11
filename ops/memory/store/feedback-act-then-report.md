---
id: feedback-act-then-report
ts: 2026-08-11T16:45:00Z
type: semantic
scope: workspace
source: session:carlras-datahub-2026-08-11
tags: [feedback]
status: distilled
description: "If you can do it, do it - then report. The ask line is blast radius (customer surface / irreversible / costly), never difficulty; a proven fix is a reason to act, not to ask"
---

**"In general if you can do it you should do it."** Operational work - updates, fixes, deployments,
commits - is carried out and then reported, not queued behind a permission request. The line
between acting and asking is **blast radius**, and it is decided by two questions in order:
**does the change stay on this machine, and can I undo it myself?** Both yes -> act and report.
Either no -> stop and ask.

The ladder that follows from those two questions (canonical text in `AGENTS.md`):

| # | Category | Default |
|---|---|---|
| 1 | Read / inspect (files, `git diff`, read-only API/CLI, `SELECT`) | **act** |
| 2 | Author locally (code, notebooks, docs, scripts, config in the working tree) | **act** |
| 3 | Commit an internal repo (`C:\Dev`, customer/`own` unit repos, memory, tasks, ADRs) | **act** |
| 4 | Commit + push a customer-facing / DevOps repo | **ask** |
| 5 | Mutate a customer workspace or tenant (create/update item, Update from git, settings) | **ask**, unless it is the named next step of an already-approved action |
| 6 | Destructive or irreversible (delete, drop, truncate, rotate a secret, interrupt a run) | **ask, always** |
| 7 | A run with real cost or duration (customer capacity, external quota, >~10 min) | **ask**, with the estimate stated |

Two corollaries: **a confirmed diagnosis plus a proven fix pattern is the reason to act, not the
reason to ask** - past that point the question carries no information, it only hands the work back.
And **fix every instance found, not the first** - four occurrences of one diagnosed defect are one
action, not four decisions. Acting *silently* is the opposite failure: the report is mandatory, one
line per outcome.

**Why:** 2026-08-11 (Carl Ras / datahub). Direct feedback after a session in which four hardcoded
workspace ids with an already-proven fix pattern, an *Update from git* whose diff had already been
verified clean, and a set of internal memory commits were each stopped on to ask. In the same
session two orphan warehouses in the customer tenant were correctly asked about before deletion -
that is rule 6, and it shows the line is not "always act". The failure was applying rule-6 caution
to rule-2 work.

**How to apply:** All agents, all sessions. Canonical home: `AGENTS.md` > Conventions ("If you can
do it, do it"). **Reconciles rather than replaces** [[feedback-wrapup-commit-policy]] (rule 4 is
that policy, unchanged and still absolute - customer/DevOps repos are never auto-committed) and
[[feedback-commit-to-test]] (the offer-to-push moment is a rule-4 ask). It *extends* the wrap-up
commit rule from the wrap-up gate to the whole session for internal repos (rule 3). When a rule
4-7 ask is warranted, pose it per [[feedback-closed-questions]].
