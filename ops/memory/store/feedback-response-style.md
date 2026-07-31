---
id: feedback-response-style
ts: 2026-06-15T14:47:15Z
type: semantic
scope: workspace
source: session:e678d0ab-d775-4bf3-9008-853956d8e8f8
tags: [feedback]
status: distilled
description: "Response verbosity control (terse/brief/full steering words) and default to no edit narration"
---

User steers response length with sticky keywords: **terse** (answer/result first, minimal prose, no preamble/recap), **brief** (short answer + 1-2 lines essential context), **full** (detailed explanations, surfaced reasoning). A keyword stays in effect until the user changes it. Default when unset: **brief**.

Standing default: **no edit narration** — state outcomes ("Updated X to do Y"), don't walk through line-by-line changes or show snippets unless asked. User trusts the diff.

**Why:** User finds full-detail edit walkthroughs and large text volume overwhelming; the right level varies by what we're doing, so on-demand control beats a fixed setting.

**How to apply:** Honor the latest keyword for all subsequent replies. Keep formatting tight (short sections, scannable). Surface edits as one-line outcomes. Expand only on request or via `full`. See [[feedback-design-dialogue]].

## "Plainly" means prose, not structure (added 2026-07-31)

When the user asks to have something explained **plainly** / "in plain speak" / "explain to me why", the answer must be **connected prose in ordinary words** — no bold headers, no bullet lists, no tables, no `file:line` citations, no **[VERIFIED]**-style tags. Those belong in written design docs, not in an explanation. Typically 1-3 short paragraphs.

**Why:** Caught 2026-07-31 (Carl Ras / Marketo). Asked "explain to me plainly why you need to check `updatedAt`", the reply came back with bold section headers, a doc citation and field-name jargon. The user's response: *"is that plain speak for you? then we need to adjust your behaviour."* Structured formatting reads as a report, not an answer — it is the same overwhelm problem as verbosity, in a different dimension.

**How to apply:** Treat "plainly" as a format instruction, not just a length one. Say the thing in the words you would use out loud. Keep the precise field/file names only where getting them wrong would mislead. Structure is for documents; conversation gets sentences. See [[feedback-fact-only-language]] — plain wording must still not overstate the evidence.
