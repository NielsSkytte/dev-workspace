---
id: eval-20260913-chrome-skill-not-invoked
ts: 2026-09-13T20:52:00Z
type: evaluative
scope: workspace
source: session:0f971801
tags: [skill-evaluation, claude-in-chrome, verification]
status: distilled
description: "The claude-in-chrome skill did not fire before browser verification of a 15 MB lineage report; the attempt cost ~10 turns of failed screenshots and was abandoned without a visual confirmation"
---

**Should have fired and did not:** `claude-in-chrome`. Its own description says to invoke it
BEFORE any `mcp__claude-in-chrome__*` tool. The tools were loaded straight from `ToolSearch` and
the skill was never called.

**What happened:** verifying a new hover tooltip in the MetaAtomic lineage report meant opening a
15 MB self-contained HTML page. `file://` was refused, so the page was served over
`127.0.0.1`. From there: `Page.captureScreenshot` timed out repeatedly on the full report,
`javascript_tool` could not see page globals (isolated world), and the viewport came back
955x520 no matter what `resize_window` was given, leaving the graph canvas a few pixels tall
under a fixed header. A subset report was built to shrink the page, which did render and did
expose a real defect (a JS `SyntaxError` from a newline written into the generated script), but
the tooltip itself was never seen. Verification fell back to a clean console read plus the
engine tests.

**Whether the skill would have helped is not known** - it was not read. What IS known is that the
built-in rabbit-hole rule ("stop after 2-3 failing browser calls and ask") was passed by several
turns before the attempt was abandoned.

Worth checking at the next browser task whether the skill carries anything on capture timeouts
on large pages or on reading page state from an isolated world.
