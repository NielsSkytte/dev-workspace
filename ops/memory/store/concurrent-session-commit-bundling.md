---
id: concurrent-session-commit-bundling
ts: 2026-08-19T10:30:00Z
type: semantic
scope: workspace
source: session:3582ea00-1223-4496-8acc-d74e4a5b233d
tags: [git, workflow, sessions]
status: distilled
description: "Two Claude sessions in one repo share a working tree - one session's commit swept up the other's staged-but-uncommitted fix and pushed it under an unrelated message"
---

Niels runs several sessions at once, and they share the working tree of any repo both touch.

**What happened (2026-08-19, `Semantic-Model`).** This session edited
`Model.SemanticModel/definition/tables/Campaign Forecasts.tmdl` (one line, Currency fix) and left
it uncommitted, pending approval to push a customer repo. A concurrent Direct Lake session then
committed its own work as `503b5d4` *"Model_OneLake: pure Direct Lake - no Import tables left"* and
pushed — carrying the Currency fix with it, under a message that says nothing about it.

Outcome was benign (the fix needed pushing anyway, and it landed) but it was not a decision anyone
made, and the customer-repo approval gate was bypassed as a side effect.

## What follows

- **Read `git status` immediately before committing**, and commit by path when the tree may hold
  another session's work. Never `git commit -a` in a repo two sessions are in.
- **A file left uncommitted is not a hold.** If a change must not ship yet, it needs to be out of
  the working tree (stash / branch), not merely unstaged.
- **Re-check ownership before claiming a push.** Verifying "is it pushed" here meant
  `git log origin/main..main` (empty) plus reading the commit that actually contains the line —
  the commit message was no guide at all.
