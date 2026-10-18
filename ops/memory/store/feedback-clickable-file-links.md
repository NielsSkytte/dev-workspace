---
id: feedback-clickable-file-links
ts: 2026-10-16T12:30:00Z
type: semantic
scope: workspace
source: session:78a2d310-6388-447e-b137-3d87b961156c
tags: [feedback]
status: distilled
description: "A file Niels should open is given as a clickable markdown link with a file:/// URL, not a bare or relative path; only files he needs to see, not every changed code file"
---

Give every file Niels should open (HTML page, report, draft, diagram) as a markdown link with a
`file:///` URL: `[progress.html](file:///C:/Dev/customers/Carl-Ras/process-insight/design/progress.html)`.
Forward slashes, spaces encoded as `%20`. A published artifact also gets its claude.ai URL.

**Why:** 2026-10-16 - short relative paths (`design/progress.html`) did not render as links and did
not say where the file was; he had to ask for the links. He then asked for links only to "the stuff
I need to see", not every code file touched.

**How to apply:** links for deliverables to open; changed code files are named once as a full path,
or not at all if the change is reported as an outcome. Rule also in `C:\Dev\CLAUDE.md` > Behaviour.
See [[feedback-response-style]].
