---
id: feedback-update-other-repo-first
ts: 2026-11-26T11:30:00Z
type: semantic
scope: workspace
source: session:processinsight-2026-11-26
tags: [feedback]
status: distilled
description: "Before basing any work on a repo outside the one the session works in: fetch, check branch and how far behind, fast-forward the default branch when the tree is clean, then read; cite the commit read"
---

**Rule (Niels, 2026-11-26, addressed to M):** whenever work of any kind is based on a repo other than
the one the session works in, always check the state of that repo and update it before looking at
its content.

Steps: `git fetch --all --prune`; `git status -sb`; note the branch and how far it is behind its
upstream and the default branch. Clean tree: switch to the default branch (or the branch the work
names) and `git merge --ff-only`. Local changes or a branch ahead: do not switch; tell Niels the state
and which commit was read. Findings cite the commit.

Why: an analysis of Mads's model scripts read `C:\Dev\pingala\AtomicVision` on the branch
`processinsight/c2r-house-star`, 94 commits behind `main`; the Metric Library table there had 20
columns, on `main` 30. Canonical text: `AGENTS.md` > Conventions.
