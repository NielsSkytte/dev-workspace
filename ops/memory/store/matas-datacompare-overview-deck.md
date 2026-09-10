---
id: matas-datacompare-overview-deck
ts: 2026-09-10T00:00:00Z
type: semantic
scope: project:customers/Matas/DataCompare
source: /log
tags: [matas, datacompare, presentation, deck, pingala-visual-identity, html]
description: The DataCompare overview deck - where it lives, how it is built, what is hidden in it.
status: distilled
---

`customers/Matas/DataCompare/design/presentation/` holds the customer-facing overview of what
DataCompare is and does. Eight slides, plain English, Pingala visual identity.

- `datacompare-overview.src.html` is the **source**. It carries `{{ICON}}` tokens where a brand
  SVG belongs.
- `build.py` inlines those SVGs as base64 data URIs from the `pingala-visual-identity` skill's
  asset folders and writes `datacompare-overview.html`, which is self-contained and makes no
  external request. Edit the source, run `python build.py`, never edit the built file.
- Slides: title, purpose, the end-to-end picture, how one field is compared, how a rule is made and
  undone, what the first runs found, adding a system or an entity, where it runs. Arrow keys
  advance; Ctrl+P renders a PDF.
- An **executive-brief slide is commented out** in the source (marked `hidden 2026-09-10, owner`),
  not deleted. Uncomment the block to bring it back.
- Diagram slides carry the class `diagram`: the SVG scales down to whatever vertical space is left,
  so a slide never spills past the viewport.
- Every number on a slide comes from a real run. One illustrative count was removed when the figure
  captions were dropped, because the caption was the only thing marking it as illustrative.
