---
id: eval-20260902-skill-in-window-context
ts: 2026-09-02T16:00:00Z
type: evaluative
scope: workspace
source: session:e15b57a5
tags: [workspace, skills, fno, evaluation, bonus]
status: distilled
description: "fno-time-registration was live and on-topic all day and never fired - defensible only because the session had authored its contents hours earlier, which is exactly the reasoning to distrust"
---

**Skill-evaluation checkpoint for 2026-09-02.** `fno-time-registration` was live from the start of
the day, its description matches every topic the session touched — F&O registration, the utilisation
page, per-customer dimensions — and it **never fired**. Neither did `/fno`.

**The defence, and why it is only half good.** This session *authored* the skill's contents the day
before; everything in it was already in the context window, so loading it would have been redundant
here. That is true, and it is also precisely the reasoning that lets a skill quietly stop being used.
The test is not "did I already know this" but "would the next session, cold, have needed it" — and
the answer is plainly yes. Two of today's three findings landed in the skill *because* it exists to
hold them.

**The skill accumulated correctly, which is the real signal.** Neither of today's durable rules
existed when it was built yesterday:

- the **bonus model** (`bonus-model-faktureringsprocent`) and the `/fno` gate that runs it, and
- **Element Logic's `Beskrivelse`**, which finally placed the `45394` that had sat unexplained in the
  sheet since July.

A capability built one day and extended the next on real work is behaving as intended. The failure
mode to watch is the opposite one: a skill whose knowledge only ever grows in the session that wrote
it.

**Two self-inflicted defects, both caught the same day, both worth the pattern.**

- `dashboard.html` *Copy rows* filtered on company while the table above it filtered on company
  **and** the customer chips. Copying with a customer deselected put extra rows on the clipboard,
  invisibly — an over-registration into a production ERP. Found by Q while reading the page for
  unrelated reasons. **A read-only pass over code for one purpose is a good time to notice another.**
- `bonus.py` pointed a fresh month at the 50% boundary, which pays 0%. Correct arithmetic, useless
  advice. Surfaced only because real data (September, empty) was run through it. **Test a new tool on
  the boring inputs, not only the interesting one.**

**And one reasoning error worth more than either.** Yesterday's 33,00 h on a lagging utilisation page
was treated as evidence of a *second source* of posted time, raising a false double-registration
alarm. The premise — that the page was current — was never established. See
`fno-month-close-approve-not-post`. **A stale number is not a second number.**
