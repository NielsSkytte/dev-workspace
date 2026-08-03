---
id: eval-2026-08-03-fno-entry-page
ts: 2026-08-03T09:05:00Z
type: evaluative
scope: workspace
source: session:972e353e
tags: [evaluative, dashboard, time-tracking, fact-only-language, memory-summarizer]
status: distilled
description: "evaluative: four UI defects shipped and reported by the user before I caught them - all affordance/visibility, not logic; invariants (period total, day cap) caught the two data bugs"
---

Session 972e353e, 2026-08-01 -> 08-03: the F&O entry page and timesheet views.

## The pattern worth keeping

**Every defect the user reported was about affordance or visibility. Every defect I caught myself
was logic.** Four the user had to report:

1. The internal-hours panel behind a tile-footer link whose hover state was light-on-light --
   invisible; they read the alert rows as the panel.
2. "Clicking July only shows PING" -- all four company blocks rendered, but PING's 49-row table was
   ~1400px in an 822px viewport, so nothing below it existed as far as the user could tell.
3. Company pills built as **jump links** when the user wanted **filters** -- clicking scrolled the
   bar out of view, leaving no way to see or undo the selection.
4. Header links coloured `--brand-2` on the `--brand` header: brown on teal.

Two I caught myself, both by checking an **invariant** rather than reading code:
- The 3.50 h phantom from a dict that overwrote casing variants -- caught because the period total
  must not change when time only moves sides.
- The 15 h day from raising the merge threshold to 5 h -- caught by asserting no day exceeds
  `DAY_CAP` after the change.

**Lesson:** logic gets verified because I have invariants to test it against; presentation does not,
so it ships broken. When adding a control, state what it is (filter? link? action?) and check it is
*visible and reversible* before calling it done. A screenshot would have caught all four; the browser
tooling was flaky for most of this session and I leaned on DOM assertions, which confirm structure
and say nothing about whether a human can see or use it.

## A CSS trap worth remembering

`<div style="overflow-x:auto">` computes to `overflow-y: auto` -- setting one axis promotes the
other from `visible`. Every table wrapper became a vertical scroll container with nothing to scroll,
swallowing the wheel; dragging the scrollbar still worked because that targets the real container.
That asymmetry ("works when I drag it, not with the wheel") is the signature. Always set both axes.

## Local summarizer

`20260801T125739Z` records "**Entered** internal time for July 2026" for a turn that entered
nothing -- it built the page and reported that 13.25 h had no company. Fourth consecutive `/log`
with the summarizer asserting a completed action that did not happen. This is no longer a per-day
vetting problem; the model or prompt needs changing.

Also confirmed: the capture hook recorded the **`/log` command's expanded help text as the User
body** on three turns -- the same defect already logged in `ops/TODO.md` for `/handoff`, so it is
not command-specific.

## Skills

No workspace skill fired, and none should have -- the subject was the harness (dashboard, rollup,
timesheets). `/dashboard` and `/log` fired on invocation.
