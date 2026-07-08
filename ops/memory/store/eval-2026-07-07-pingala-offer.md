---
id: eval-2026-07-07-pingala-offer
ts: 2026-07-08T00:00:00Z
type: evaluative
scope: project:customers/Aeven/ServiceNowPOC
source: session:003da8cc (/log distill)
tags: [skill-evaluation, pingala-offer, fill-sow, writing-voice]
status: distilled
description: "Evaluative 2026-07-07 Aeven offer finalisation: pingala-offer fired+helped; /fill-sow recipe worked but lacked a Word-open verification step; writing-voice not loaded (borderline)"
---

Skill observations from the Aeven ServiceNow POC offer finalisation (SoW v0.4 -> v1.0 docx+PDF):

- **pingala-offer: fired, helped.** Loaded on "finalise the offer". The doctrine acted as
  verification gates, not just writing guidance: the zero-"?" check and no-placeholder rule were
  run mechanically against the final PDF text; "content unchanged, expansion via the Q4 option"
  meant no re-litigation of the reviewed draft; licensing exposure was placed into the scope
  table at budget-holder altitude.
- **/fill-sow: followed as recipe, mostly accurate** (section->cell mapping table matched the
  real template). Gap: the recipe verifies nothing after the fill — its own tool had two bugs
  that made every output either un-openable in Word (empty-cell corruption) or silently wrong on
  reopen (data-bound customer name). Both invisible without opening the result in Word. The tool
  is fixed (see `sow-fill-toolchain`); consider adding a "verify: open via Word COM + placeholder
  probe" step to the command.
- **writing-voice: did not fire.** New customer-facing prose this session was one Document
  History row; the rest reused approved v0.4 text. Borderline by its own trigger ("any
  customer-facing prose qualifies") — no observed harm, but a fuller redraft session must load it.
