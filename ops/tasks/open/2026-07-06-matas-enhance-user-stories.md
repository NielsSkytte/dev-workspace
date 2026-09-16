---
title: Enhance the existing Matas user stories in DevOps (DataCompare)
status: open
created: 2026-07-06
project: customers/Matas/DataCompare
owner: self             # story enhancement = Niels judgment; content agent can draft
priority: normal
blocked_by:
activity: 111953        # F&O activity for 212-01 (owner, 2026-09-07)
fno_task: Task-65905    # opgave = the configuration work (Link to Fabric, access, setup); 65904 is the engine and app work (owner, 2026-09-08)
customer_ask: none
waiting_on:
resume_on:
source: todo
---

## What
Enhance the user stories that already exist in Matas's own Azure DevOps setup for the DataCompare
project — more detail on project design, acceptance criteria, etc. Matas controls the story setup;
we do NOT create a parallel backlog (discovered 2026-07-06: everything is in place in DevOps,
enhancement is the work).

## Progress

**Now (2026-08-31):** no story has been enhanced yet. The task exists as the F&O binder for
configuration time (`Task-65905`, activity 111953); all 23.00 h of Matas time registered up to
08-31 was assigned across the two ADO tasks (17.50 h to 65905, 5.50 h to 65904). Engine and app work
moved to `2026-09-08-matas-datacompare-engine-app` on 09-08.

**Tried and dropped:** authoring our own backlog -> enhancing Matas's existing stories (Matas owns the
story setup, found 07-06).

**Next:**
1. Read the DataCompare stories in Matas's DevOps and list which lack design detail or acceptance
   criteria.
2. Draft the enhancements (content agent can draft; Niels decides) and apply them in DevOps.

## Needs from customer

- none

## Why
The stories are the delivery contract for DataCompare. This task is also the **/switch-task binder**
for Matas sessions — Matas (212-01) bills per ADO Task, so Matas work must run under a started task.

## Context
- Doctrine: AGENTS.md > Continuity loop — DevOps is the backlog; this task is the thin F&O binder.
- Project: `customers/Matas/DataCompare` (fno_code 212-01).
- Matas has two ADO Tasks that all 212-01 time lands on:
  - `Task-65905` **Configuration of PoC** — environment setup, Dataverse sync, access, capacity,
    link/table scope, environment discovery.
  - `Task-65904` **Design** — the comparison engine. **Does not exist in F&O** (checked 2026-09-01;
    F&O: "Opgaven eksisterer ikke - nye opgaver bør oprettes via DevOps"). All time originally
    mapped to it now books to `Task-65905` per Niels, until the task is created in DevOps.

## Log
- 2026-07-06 — created at the v1 triage (was TODO 2026-06-19 "write up the user stories...";
  reshaped after discovering Matas owns the story setup — enhance, don't author).
- 2026-08-31 — Activity question closed: F&O fills it automatically, nothing to supply. The two ADO
  Tasks above were given by Niels and all 23.00 h of registered Matas time was assigned across them
  (17.50 h to 65905, 5.50 h to 65904).
- 2026-09-16 — brought onto the Progress shape (Progress + Needs from customer, fno_task Task-65905, customer_ask none); no facts changed. Card: CONTEXT.md converted to the resume card.
