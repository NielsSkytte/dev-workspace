---
id: time-value-records-die-with-the-transcripts
ts: 2026-09-08T12:45:00Z
type: semantic
scope: workspace
source: /log
tags: [time, value-model, adr-004, evidence, transcripts, billing]
status: distilled
description: "The weighted-hours record for a day can only be derived while its session transcript still exists, and Claude Code keeps roughly 30 days. Found 2026-09-08: of 16 billed Matas days in July and August, only 9 have a value record, and the other 7 can never get one - value.py --month returns nothing for July and omits Matas for August because those transcripts are gone. A billed day without a value record has no evidence behind its charge and cannot be reconstructed"
---

**How it surfaced.** The owner suspected the July/August weighted numbers were wrong. They were not
wrong, they were incomplete: 18.75 h billed across 16 days, weighted records covering 9 of them
(28.00 h). The remaining 7 days had to be estimated - keyboard time from the heartbeats (which do
survive) times the 7.26x factor measured on the recorded July days.

**The lesson for the loop.** /log must run inside the transcript window, weekly at worst; a
month-end-only pass loses days permanently. A guard is wanted: warn when a billed day has no
ops/time/value/ record while its transcript is still on disk. Heartbeats are not a substitute - they
carry attribution and clock time, never the evidence of what was done.
