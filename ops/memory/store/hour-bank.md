---
id: hour-bank
ts: 2026-11-03T16:30:00Z
type: semantic
scope: workspace
source: owner 2026-11-03, session fff04b8f
tags: [time, bank, invoicing, fno]
status: distilled
description: "Hour bank (ops/time/bank.md): hours spent but held from F&O sit on own/ projects as deposits; withdrawals place them on customer lines later"
---

Owner, 2026-11-03: a function for "hours already spent but not ready for invoicing" -- to
invoice later under customer agreements, and to save up cross-customer engine work or spread
it over time. Holding place: the `own/` project whose work it was.

- Register `ops/time/bank.md` (Deposits / Withdrawals), reader `ops/lib/bank.py`, CLI
  `python ops/bin/bank.py`, Time page "Hour bank" card. Spec: `ops/time/README.md` section 9.
- Reclaim ledger folded in as R1/R2 (fully drawn); `reclaim.md` removed.
- First deposit B1: October process-insight no-task lines, 42.75 h F&O entry (16.50 work,
  53.39 weighted), on own/ProcessInsight, for Carl Ras, terms not set.
- Recorded measure-moves now apply before the same-project attach, so banked lines keep
  their measurement.
