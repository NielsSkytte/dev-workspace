---
id: eval-2026-08-01-matas-datacompare
ts: 2026-08-01T12:46:00Z
type: evaluative
scope: project:customers/Matas/DataCompare
source: session:11777a94
tags: [evaluation, skills, pingala-fabric-platform, email-outlook-ready, fabric-project-access, process]
description: "Matas DataCompare session: skills fired only when invoked by hand; twice asserted a setup state instead of checking it with a tool already in hand"
status: distilled
---

## Skills

- `pingala-fabric-platform` and `email-outlook-ready` both **fired usefully, but only because
  I invoked them explicitly**. Neither self-triggered.
- `fabric-project-access` + `pingala-project-playbook` **were surfaced by the harness** as a
  mid-session availability reminder exactly when the subject turned to link-table scope. That
  is the trigger surface working - but I did not act on it, I answered from research already
  in context. Counts as a near-miss, not a win.
- Continues the pattern from `eval-2026-07-31-skills-available-not-firing`: at project root
  the skills are now present (harness cascade fixed in the concurrent session), and the
  remaining gap is that **presence does not produce use**.

## Own-output failures - one repeated shape

Twice I **asserted a state of the setup rather than checking it**, with the checking tool
already in hand:

1. Planned "connect ETL_Dev to git" as a step. It was **already connected**. One
   `fab api "workspaces/<id>/git/connection"` would have shown branch, directory and synced
   head. I only ran it after the user asked why the workspace was empty.
2. Told the user M was "not loadable as a subagent from this session" from the agent list in
   context, rather than treating it as a provisioning question. The concurrent session was at
   that moment fixing exactly that, and the agents appeared later in the same session.

Rule earned: **before telling the user a setup step is still needed, query the setup.** The
Fabric REST surface via `fab api` answers most of these in one call. This is the same family
as `feedback-fact-only-language` - the failure is asserting an unverified state, not the
state being wrong.

Third failure, different shape: after the user decided `fabric/` was the home for all code, I
still told them to **paste the notebook into the Fabric UI**. They had to ask "did you commit
so I can update in fabric?" to get the route that their own decision implied. A decision
recorded is not a decision applied - re-read the last decision before proposing the next step.

## Process that worked

- Verifying auth before acting became a **guardrail** (AGENTS.md 11) plus `tenant_id:` /
  `account:` on every customer node, after `fab ls` returned another customer's estate. The
  correction produced structure, not just an apology.
- `fab table schema` verified 11 tables' columns against a live tenant **without running
  anything in Fabric** - the cheap check that retired the single most fragile design
  assumption in Part 2.

## Local summarizer

Four fidelity flags in `daily/2026-07-31.md` (this session's records), consistent with the
last three /log entries: agency misattributed (user-run command reported as mine), "provided a
command to bypass" GCM when no bypass was offered, an unconfirmed MFO/GFO mapping reported as
"determined", and a repo push summarised as "Pushed a commit to GFO_DataCompare_ETL_Dev" -
conflating a git push with workspace state, which is precisely the distinction the turn was
about. **Nothing distilled as-is**; store records written from the conversation.
