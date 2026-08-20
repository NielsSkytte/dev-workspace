---
id: eval-2026-08-20-visual-identity-not-invoked
ts: 2026-08-20T00:00:00Z
type: evaluative
scope: workspace
source: session:45041831
tags: [skills, pingala-visual-identity, dataviz, evaluation, design]
status: distilled
description: "Evaluative: built a new dashboard page with a colour palette, tables and a stacked bar without invoking pingala-visual-identity or dataviz; the output complied only because dashboard.html already encodes the palette"
---

**The miss.** Built the Week audit page (`ops/dashboard.html`, route `#timesheet/audit`) — five
sections, a five-tile header, a stacked tier bar, new CSS — and invoked neither
`pingala-visual-identity` nor `dataviz`. `[[eval-2026-08-10-pingala-visual-identity-trigger]]`
records a standing mandate to load the identity skill before **any** visual output; it was not
followed. Ninth consecutive session with the domain skills silent.

**Why it did not show.** `dashboard.html` already encodes the identity in its CSS variables —
`--cta:#4D7878` (Deep Teal), `--accent:#B5442A` (Terracotta), `--plane:#EEE4DE` (Warm Cream) are
exactly the values in that 2026-08-10 record. Matching the surrounding file therefore produced a
compliant page. **Compliance by accident is not compliance by rule** — the same habit on a file
with no palette of its own would have produced a generic page, which is precisely the 08-10
failure.

**Rule earned.** When the target file already carries a design system, the correct action is still
to *check* it against the identity, not to assume the file is right: a file can drift, and only the
skill knows what the current palette is. The cheap version of the check is to read the file's
tokens and compare them to the skill's — but the comparison has to happen.

**Not a miss:** `claude-in-chrome` fired and earned it. The page was verified in a real browser
before shipping, which caught three defects a code read would not have — two run-together column
headers, today flagged `unaccounted` in red, and today counted as 7.5 h short.
