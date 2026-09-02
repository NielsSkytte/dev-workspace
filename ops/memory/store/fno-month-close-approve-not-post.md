---
id: fno-month-close-approve-not-post
ts: 2026-09-01T15:15:00Z
type: semantic
scope: workspace
source: session:e15b57a5
tags: [fno, time, month-close, journals, decision]
status: distilled
description: "Closing a month in F&O means Godkendelse -> Finished, not Bogfoer - approval leaves the journals under Ikke bogfoert and posting stays a separate later decision"
---

The August close was begun with **Bogfør** and stopped by Niels: *"tror bare du skal godkende dem"*.
The month-close step here is **Godkendelse → Finished**.

**What Finished does.** Selecting the journal row (F&O acts on the *active row*, not the checkbox)
and choosing Godkendelse → Finished raises a *"Kontroller kladde <journal>"* dialog with batch
settings; OK returns *"Kladden har ændret status til Finished."* The journals **stay visible under
"Ikke bogført"** — Finished is an approval state, not a posting. Posting is a separate, later
decision and is Niels's.

**The consequence for reporting — and the trap in it.** The utilisation page counts only **posted**
lines, *and it lags*. It read 33,00 h for August while 138,75 h sat approved-but-unposted; the next
day, with everything posted, it read the full **145,00 h**. A low utilisation figure right after a
close is expected and is not evidence of missing registration.

The 33,00 h was **our own time, partially aggregated** — but on 01-09 it was reasoned about as
evidence of *a separate source*: "that 33,00 h therefore came from lines posted outside our
journals", raising a false alarm about August being double-registered by up to 33 h. The arithmetic
that seemed to support it (W32 stood at 24,75 h when the page showed 33,00) only established that
the page disagreed with the journals — which is precisely what a lag looks like. **A stale number is
not a second number.** Before inferring a source from a total on a report, establish that the report
is current; on this page, that means waiting until everything is posted.

**August 2026 closed as** — PING `021924` W31 3,50 / `021926` W32 33,00 / `021928` W33 50,50 /
`021953` W34 46,50 / `021954` W35 4,00 / `021975` W36 1,25 = 138,75 h, all Finished; PNO1 `004431`
6,25 h already posted. **145,00 h.** The empty `PING-021923` (0,00 h) was left untouched.

**A journal is per week, per company.** One journal per ISO week in PING, named `NSC-August-W<nn>`;
Element Logic goes in its own PNO1 journal. A line that arrives after its journal is posted cannot
be added to it — the Element Logic 07-08 0,50 h line was **dropped** on instruction rather than
opening a new PNO1 journal for a single line.
