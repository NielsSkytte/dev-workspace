---
title:
status: open          # open | in-progress | done | cancelled
created:              # YYYY-MM-DD
project:              # own/X | customers/Client/Project | (blank = workspace-level)
owner:                # M routes → fabric-back | semantic | fabric-front | content | architect | Q | self
priority: normal      # low | normal | high
blocked_by:           # optional — what is blocking this
activity:             # optional — F&O activity (WBS) this task rolls under (customer projects)
fno_task:             # customer projects: the Azure DevOps work item id, or the word `none` — never left blank
customer_ask: none    # none | open (we need something, not yet sent) | sent YYYY-MM-DD | answered
waiting_on:           # parked: `customer` or a name we wait on; leaves the daily view until cleared (/task wait, /task resume)
resume_on:            # parked until this date (YYYY-MM-DD); shows as due back when it passes (/task postpone)
source: direct        # todo | inbox | direct
---

## What
<The work, in plain language. Done when: the observable end state.>

## Why
<Why it matters / what it unblocks. Skip only if truly self-evident.>

## Progress
<!-- Rewritten as the work moves; the project's CONTEXT.md task line is derived from this block. -->
**Now:** <where it stands, one to three lines, dated>
**Tried and dropped:** <what did not work and why, only where it changes the next step>
**Next:** <ordered, the immediate step first>

## Needs from customer
<!-- What the customer (or a third party) must do or answer, who, and whether it has been sent.
     Mirror the status in `customer_ask:`. "none" if nothing. -->
- 

## Context
<Refs the worker should re-read first: files, projects, ADRs, [[memory links]], related tasks.>

## Log
- YYYY-MM-DD — created
