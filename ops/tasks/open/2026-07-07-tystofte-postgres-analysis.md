---
title: Analyse Tystofte postgres data (metadata extract → review workbook)
status: open
created: 2026-07-07
project: customers/Tystofte/Data-Discovery
owner: fabric-back
priority: normal
blocked_by:
activity:
fno_task: none
customer_ask: open
waiting_on: customer
resume_on:
source: todo
---

## What
Analyse the Tystofte postgres data with the same approach as the Oracle FCS08 work: extract
metadata, then run the review-workbook flow.

## Progress

**Now (2026-07-07):** created from the TODO; not started. The FCS08 (Oracle) flow it copies is
built in Data-Discovery and Tystofte-Fabric.

**Tried and dropped:** none.

**Next:**
1. Confirm with Tystofte that the Postgres analysis is wanted now, and which database.
2. Extract the Postgres metadata the way `nb_A_build_metadata` does for FCS08, then build the
   review workbook from it.

## Needs from customer

- **Tystofte:** confirmation that the Postgres analysis is wanted, and access to the database.
  **Not asked.**

## Why
Second source in the Tystofte data-discovery track; postgres access was granted (Ravn IT,
checked off 2026-07-06). Pairs with the design-doc review in the Tystofte INBOX package.

## Context
- Project: `customers/Tystofte/Data-Discovery` (fno_code 4048-1); the Oracle FCS08 flow there is the template.
- Tystofte INBOX package (2026-07-06 triage): postgres analysis + design-doc input.
- Route to the DevOps work item when one is assigned (fill `fno_task:` then).

## Log
- 2026-07-07 — created (promoted from TODO 2026-07-06 at the day-start routing pass)
- 2026-09-16 — brought onto the Progress shape (Progress + Needs from customer, fno_task none, customer_ask open); no facts changed. Card: CONTEXT.md converted to the resume card.
- 2026-09-21 — set waiting_on: customer (ask not yet sent)
