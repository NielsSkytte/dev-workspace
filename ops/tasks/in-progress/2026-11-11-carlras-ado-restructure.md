---
title: Carl Ras - ADO backlog restructure (data platform, process insight, business areas)
status: in-progress
created: 2026-11-11
project: customers/Carl-Ras/datahub
owner: self
priority: normal
blocked_by: Carl Ras ADO admin (area paths, Shared Queries write)
activity:
fno_task: none
customer_ask: open
waiting_on:
resume_on:
source: direct
---

## What
Restructure the Carl Ras ADO project `Datahub` so data-platform work is one Feature per source, one Work Package per Feature with one `SyncToPingala` booking Task, and Process insight is its own Epic. Done when: the four area paths exist and hold their items, the business-area queries are shared, and Mads has answered on his items.

## Why
The old tree split work by medallion layer (Landing zone / Raw / Enriched), so one source had three WPs and every Task was an F&O line. Mads and Niels need one way to see and request each other's work.

## Progress
**Now (2026-11-11):** Applied in ADO: Epic 842 Process insight, Features 843-853, WP 854 + booking Task 855 (AX09: Data correctness), WP 856 + booking Task 857 (Direct Lake), work Tasks 858-862 (Process insight) and 863 (drift). 13 layer WPs and Features 43/44/45 Closed; Successor links to Mads's Features in place. Area paths AX04, Navision, Graph API, Process insight not created (TF50309, no permission): those items sit in `Data hub`. 7 queries under My Queries/Business areas (no Shared Queries write, TF401256). Design: `design/ado-restructure.html`.
**Tried and dropped:** Keeping layer WPs whole (drafts 2-3): it left several WPs per Feature. Folding Feature 713 into Process insight (draft 4): Business area is where results are delivered.
**Next:**
1. Carl Ras ADO admin creates the four area paths and grants Shared Queries write; then move the items and the 7 queries.
2. Set Original Estimate on booking Tasks 855 and 857 (created with 0).
3. Mads answers on his items (158/159 move, 526/537/538, 470, tags); mail `emails/ado-struktur-mads.md`.

## Needs from customer
- Carl Ras ADO project admin: create areas `Data hub\AX04`, `\Navision`, `\Graph API`, `\Process insight`; grant Niels write on Shared Queries. Not sent.

## Context
- `customers/Carl-Ras/datahub/design/ado-restructure.html` (draft 5, applied ids in the header)
- `customers/Carl-Ras/datahub/emails/ado-struktur-mads.md`
- F&O test 2026-11-11: Task 524 moved 518 -> 554; F&O "Formaal" and activity follow the parent WP, hours stay.

## Log
- 2026-11-11 — created; restructure applied in ADO; booking Tasks 855/857 written to the 08-14, 08-17 and 08-18 tasks
