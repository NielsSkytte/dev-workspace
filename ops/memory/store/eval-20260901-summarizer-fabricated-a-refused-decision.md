---
id: eval-20260901-summarizer-fabricated-a-refused-decision
ts: 2026-09-01T15:15:00Z
type: evaluative
scope: workspace
source: session:e15b57a5
tags: [workspace, memory, sentinel, capture, summarizer, defect, time]
status: distilled
description: "The local summarizer inverted a refused topup into a decision to enter 17,50 h - the sixth consecutive fabricated completion, and the first whose subject was money - so the day was distilled from the session rather than from the stream"
---

Sentinel vetted `daily/2026-09-01.md` (18 records) at `/log` and returned **17 flags: 2 drop, 13
re-summarize, 2 truncate, 2 clean.** Verdict: *not fit for distillation as-is.* Nothing from the
stream was distilled; the day's records were written from the session instead.

**The fabrication, sixth consecutive occurrence — and the first about money.**
`daily/2026-09-01.md:99` reads *"decided to enter 17,50 h for the F&O entry ... despite the work
time being 6,75 h."* The 17,50 h is the `--topup` figure that was **refused** (see
`time-shortfall-can-be-in-the-target`), from a turn five hours later in the day; the User line on
that record is only *"you can change the company in the top right menu"*. The summarizer inverted a
refusal into a decision to inflate billable hours, and attached it to an unrelated turn.
`:261` inverts the same day's other outcome — *"decided to not commit changes to `absence.md`"* when
the vacation rows were written and committed.

The established pattern is *subject matter discussed → action performed*
(`eval-2026-08-31-summarizer-invented-a-hook`, and the open TODO from 2026-08-03). This day extends
it: **the invented action can be the opposite of the decision actually taken**, and it can concern
what a customer is billed. Distilling `:99` unvetted would have planted "we decided to bill 17,50 h"
in the snapshot as fact.

**Numbers do not survive summarization.** Five records carry figures absent from the closed month:
a target of 125,00 (it was 155), an August total of 145,50 (it was 145,00), *"136,75 hours instead
of 145,50"* and *"8,75 hours non-reversible"* (neither exists), and a journal `PING-021923` credited
with content when it closed at 0,00 h. Treat any figure in a `daily/` record as unverified.

**A coverage gap is as dangerous as a bad record.** The stream stops at 14:35 and contains nothing
about the actual close — the correction from posting to approving, the six journals reaching
Finished, the dashboard rework, `TURN_GAP = 15.0`, the §4.1 protocol, the Task-65904 → 65905 retag.
Distilled from the stream alone, August would have entered `store/` as **"booked"**, which is wrong.
Sentinel flagged this itself, outside its per-record verdicts. **Check what the stream is missing,
not only what it got wrong** — the last turns of a session are the ones that record the outcome, and
they are the ones the capture hook is least likely to hold.
