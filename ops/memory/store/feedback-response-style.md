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
