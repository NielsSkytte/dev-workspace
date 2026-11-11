---
id: feedback-no-artifacts
ts: 2026-11-05T18:00:00Z
type: semantic
scope: workspace
source: session:75e7fe1a-d272-4bb0-accb-daa75e374f9c
tags: [feedback]
status: distilled
description: "Never publish claude.ai artifacts (pages, slide decks); every deliverable is a file in a repo - a standalone .html page, a .md, a .pptx - committed where the project lives"
---

Do not use the Artifact tool for deliverables: no published pages, no Slides decks, no claude.ai links.
Write the deliverable as a file in the project's repo (a standalone `.html` with its own doctype and
head, a `.md`, a `.pptx` when asked) and commit it there.

**Why:** 2026-11-05 - a presentation for Kresten was made as a Slides artifact and an HTML artifact;
Niels: "save it as html not an artifact, never want those, all must be something we can commit to a repo".

**How to apply:** this overrides the Artifact tool's own guidance to publish. Give the file as a
`file:///` link (feedback-clickable-file-links). A shared room repo is the place for anything
the other person needs.
