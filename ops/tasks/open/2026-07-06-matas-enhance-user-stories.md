---
title: Enhance the existing Matas user stories in DevOps (DataCompare)
status: open
created: 2026-07-06
project: customers/Matas/DataCompare
owner: self             # story enhancement = Niels judgment; content agent can draft
priority: normal
blocked_by:
activity:               # none - F&O fills the Activity automatically on 212-01 (2026-08-31)
fno_task: Task-65905    # the only 212-01 task that exists in F&O (65904 was never created)
source: todo
---

## What
Enhance the user stories that already exist in Matas's own Azure DevOps setup for the DataCompare
project — more detail on project design, acceptance criteria, etc. Matas controls the story setup;
we do NOT create a parallel backlog (discovered 2026-07-06: everything is in place in DevOps,
enhancement is the work).

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
