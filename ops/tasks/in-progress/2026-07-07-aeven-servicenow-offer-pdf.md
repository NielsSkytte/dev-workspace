---
title: Aeven — formal ServiceNow POC offer in PDF
status: in-progress
created: 2026-07-07
project: customers/Aeven/ServiceNowPOC
owner: content
priority: normal
blocked_by: signed SoW returned from Aeven
activity:
fno_task: none
customer_ask: none
waiting_on:
resume_on:
source: todo
---

## What
Produce the formal Aeven ServiceNow POC offer as a PDF.

## Progress

**Now (2026-09-12):** the offer went out as SoW v1.1 on 2026-07-28 (work-order template, General
Terms, new-customer appendix) and the engagement is signed: the build runs as
`customers/Aeven/AtomicServiceNow` under F&O 4058-1 since 2026-09-12. Nothing remains here.

**Tried and dropped:** none.

**Next:**
1. Close this task as done (owner confirms); the 09-13 hours tagged to it are corrected at the
   next rollup.

## Needs from customer

- none

## Why
The offer is the gate to the Q3 engagement; `fno_code:` is created only after signature.

## Context
- Project: `customers/Aeven/ServiceNowPOC`; draft `offer/Aeven_ServiceNow_POC_SoW.md` is at
  v0.4, signable-lean (sessions log 2026-06-29 S3).
- Flow: review → fill legal name/contacts → `/fill-sow` for the Word doc → PDF.
- Skills: `pingala-offer`, `writing-voice`; doc history/version bump on any major revision.

## Log
- 2026-07-07 — created (promoted from TODO 2026-07-06 at the day-start routing pass)
- 2026-07-07 — review feedback in (content fine; hours possibly low, expansion deferred to the
  Q4 follow-on). SoW md bumped v0.4 → v1.0. Word doc + PDF rendered via /fill-sow toolchain:
  `offer/Aeven_ServiceNow_POC_SoW_v1.0.docx` / `.pdf`. Legal name Aeven A/S; contacts Niels
  Skytte (Pingala) + Aeven contact yellow-flagged (name not provided); Brøndby/Ballerup.
  Remaining: fill the Aeven contact, re-export PDF, send.
- 2026-07-28 — Aeven contact obtained; SoW re-issued as v1.1 (Pingala work-order template,
  content unchanged from v1.0) packaged with General Terms and Conditions + new-customer
  appendix, sent to Aeven. Now awaiting signed SoW returned from Aeven.
- 2026-09-16 — brought onto the Progress shape (Progress + Needs from customer, fno_task none, customer_ask none); no facts changed. Card: CONTEXT.md converted to the resume card.
