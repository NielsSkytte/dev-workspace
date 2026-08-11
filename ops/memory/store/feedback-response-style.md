---
id: feedback-response-style
ts: 2026-06-15T14:47:15Z
type: semantic
scope: workspace
source: session:e678d0ab-d775-4bf3-9008-853956d8e8f8
tags: [feedback]
status: distilled
description: "Response verbosity control (terse/brief/full steering words), no edit narration, and the standing rule: report the outcome and the decision, never the journey"
---

User steers response length with sticky keywords: **terse** (answer/result first, minimal prose, no preamble/recap), **brief** (short answer + 1-2 lines essential context), **full** (detailed explanations, surfaced reasoning). A keyword stays in effect until the user changes it. Default when unset: **brief**.

Standing default: **no edit narration** — state outcomes ("Updated X to do Y"), don't walk through line-by-line changes or show snippets unless asked. User trusts the diff.

**Why:** User finds full-detail edit walkthroughs and large text volume overwhelming; the right level varies by what we're doing, so on-demand control beats a fixed setting.

**How to apply:** Honor the latest keyword for all subsequent replies. Keep formatting tight (short sections, scannable). Surface edits as one-line outcomes. Expand only on request or via `full`. See [[feedback-design-dialogue]].

## Outcome, not the journey (added 2026-08-11 — the strongest form of this preference)

**Every reply answers three things and stops: what changed, what it means for the user, what is needed from him.** Nothing else earns space.

Cut, always, unless the user asks: how the problem was found; what was tried first; why option A over option B; a recap of the investigation; a summary of what a subagent went through; restating the user's own words back to him; and the reasoning behind a fix that already works. He trusts the work. He is deciding, not reviewing.

Findings appear only as the one line that changes his decision. "The Marketo endpoint has not published the tables yet, so deploying now would fail" is the finding. The four queries that established it are not.

**Why:** Said directly 2026-08-11 (Carl Ras / datahub), after a session of long process write-ups: *"i need to decide on next action, not get a long explanation on why we are were we are at… its like having a very talented junior dev that wants to explain everything he has been thinking about, why he chose a or b, why this was a problem, why he solved x y z — and then in the end could just have said: i fixed it, the problem was x, should i just go ahead and fix it or do you want to do something else."* Explicitly general: *"its not just this conversation, its all of them."* This is the third recorded instance of the same complaint (2026-06-15 verbosity, 2026-07-31 structure, now narration), so treat it as a hard default and not a dial.

**How to apply:** Draft the reply, then delete every sentence that is not an outcome, an implication, or an ask. If a section explains *why you did something you already did*, delete the section. Length follows from that test, not from a word budget — three sentences is a normal reply. Depth is available on request (`full`, "walk me through it", "why did you…"), and only then. Pairs with `feedback-act-then-report` (act, then report *briefly*) and `feedback-closed-questions` (the ask is the recommendation plus what "yes" triggers).

## "Plainly" means prose, not structure (added 2026-07-31)

When the user asks to have something explained **plainly** / "in plain speak" / "explain to me why", the answer must be **connected prose in ordinary words** — no bold headers, no bullet lists, no tables, no `file:line` citations, no **[VERIFIED]**-style tags. Those belong in written design docs, not in an explanation. Typically 1-3 short paragraphs.

**Why:** Caught 2026-07-31 (Carl Ras / Marketo). Asked "explain to me plainly why you need to check `updatedAt`", the reply came back with bold section headers, a doc citation and field-name jargon. The user's response: *"is that plain speak for you? then we need to adjust your behaviour."* Structured formatting reads as a report, not an answer — it is the same overwhelm problem as verbosity, in a different dimension.

**How to apply:** Treat "plainly" as a format instruction, not just a length one. Say the thing in the words you would use out loud. Keep the precise field/file names only where getting them wrong would mislead. Structure is for documents; conversation gets sentences. See [[feedback-fact-only-language]] — plain wording must still not overstate the evidence.
