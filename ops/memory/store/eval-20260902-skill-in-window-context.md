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

**The summarizer inverted a finding for the third consecutive day.** Sentinel returned 11 flags on
`daily/2026-09-02.md`, 4 fidelity failures in this session's 5 records. Two were marked `rejected`
in place:

- `:231` — *"taking a vacation reduces the monthly target"*, the direct negation of the day's central
  finding, on the very turn where Niels confirmed the per-month rule. The ~118 h it cites is the
  *hypothetical* had vacation been deducted; it was not.
- `:19` — *"identifying duplicate entries"* on the turn that **refuted** double registration, with
  the decisive 145,00 h dropped entirely.

Both concern money, as did 01-09's fabricated decision to bill a refused topup. The pattern is now
specific enough to name: **the summarizer preserves the topic and loses the polarity**, and it does
so most readily on turns where the user's message is short (`"regnes per måned"`) and the finding
lives in the assistant's reasoning rather than the prompt. Short user turns carrying big conclusions
are the ones to vet hardest. Nothing was distilled from the stream on any of the three days — the
store records were written from session context — which is the only reason none of it landed.

**Acted on the same day: turn-capture summarization is off** (`SUMMARIZE` in `capture_turn.py`,
default off; `MEMORY_SUMMARIZE=1` re-enables). `daily/` now holds the assistant's own words,
truncated to 700 chars — the fallback that already existed for when Ollama was unreachable is now
the only path. Verbatim text cannot invert a finding.

The deciding argument was not that the model is bad but that **the check was unbuildable**.
`sanitize_summary()` tests length, script and instruction-shape; a flipped polarity passes all
three, and there is no deterministic test for whether a claim is true. The only gate was a full
sentinel agent pass every `/log` — real cost, every session, forever — to protect an artefact that
had contributed **zero** `store/` records in three days. Compactness was its sole advantage, and
`daily/` is an archive nothing reads automatically.

Ollama stays: `own/MetaAtomic/lineage_engine/describe.py` uses it for the Element Logic lineage
descriptions. Sentinel's role was rewritten to point there instead, carrying the polarity lesson
with it — **read for direction, not just subject.**
