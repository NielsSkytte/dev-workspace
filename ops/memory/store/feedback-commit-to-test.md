---
id: feedback-commit-to-test
ts: 2026-06-15T15:15:24Z
type: semantic
scope: workspace
source: session:493c870d-b339-4c99-91a0-704b3cde4b70
tags: [feedback]
status: distilled
description: "Proactively offer commit+push when a push is the prerequisite to test/deploy; user still approves"
---

When local changes reach the point where committing + pushing is the *prerequisite for the next action* — testing/running them where pushed code is consumed (Git-synced Fabric via *Source control -> Update*, a CI run, a deploy, a cross-repo handoff) — proactively offer to commit and push at that moment, as a prompt the user approves. Don't push silently; don't sit on a finished change waiting to be told. The user's explicit OK is always required before any commit/push. Not a "checkpoint every change" rule — the trigger is specifically "a push unblocks testing/deploy/handoff."

**Why:** A Fabric notebook edit (2026-06-15) sat uncommitted, so Fabric showed no update to test — the workflow stalled because the offer never came. Reactive-only ("commit when asked") is too passive; silent auto-push is too aggressive. The right point is the moment a push unblocks the next step.

**How to apply:** Generic across all projects and agents; owned by M. Canonical home: `C:\dev\AGENTS.md` > Conventions ("Offer the commit-to-test..."). Relates to the Fabric edit loop [[fabric-notebook-edit-loop]] and response style [[feedback-response-style]].
