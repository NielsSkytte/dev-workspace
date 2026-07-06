---
title:
status: open          # open | in-progress | done | cancelled
created:              # YYYY-MM-DD
project:              # own/X | customers/Client/Project | (blank = workspace-level)
owner:                # M routes → fabric | content | architect | Q | self
priority: normal      # low | normal | high
blocked_by:           # optional — what is blocking this
activity:             # optional — F&O activity (WBS) this task rolls under (customer projects)
fno_task:             # optional — F&O Task id = the linked Azure DevOps work item (task-level projects)
source: direct        # todo | inbox | direct
---

## What
<The work, in plain language.>

## Why
<Why it matters / what it unblocks. Skip only if truly self-evident.>

## Context
<Refs the worker should re-read first: files, projects, ADRs, [[memory links]], related tasks.>

## Log
- YYYY-MM-DD — created
