---
id: skill-pingala-offer
ts: 2026-06-25T10:50:00Z
type: semantic
scope: workspace
source: /log
tags: [project, skill, offer, feedback]
status: distilled
description: "pingala-offer skill - trusted-advisor offer doctrine: no questions/decisions to the customer, keep the build out, customer-state interview, write for the budget holder, never state capacity location"
---

`.claude/skills/pingala-offer/` carries the **stance and structure** of a Pingala customer offer
(SoW, proposal, work order). The voice is `writing-voice`; the facts are `fabric-licensing`; this
skill is the doctrine on top.

The doctrine (all from Niels's own corrections):

- **Trusted-advisor stance:** never hand the customer a question or a decision - the count of "?"
  in an offer is **zero**; Pingala makes the call. The only exception is a sign-off only the
  customer can legally give (e.g. data residency), framed as one named prerequisite.
- **Keep the build out:** security/billing/admin/SDK/DAX mechanics are design-doc material.
- **Write for the budget holder, not the engineer:** business altitude; cut technical depth, but
  never thin out cost/licensing exposure (state what scales with use, in business terms).
- **Know the customer first:** an interview (new vs existing; what Pingala already built/runs). For
  an existing customer, prerequisites list **only** genuinely customer-side items - never the
  model, workspaces, capacity, or XMLA Pingala already delivered.
- **Never state where the capacity sits** (name "F4", not its region/placement).
- A **required-sections checklist** so a from-scratch draft does not drop the DPA/General-Terms/
  Organisation/prerequisites furniture.

Validated by consolidating the Melbye SoW to v1.0. See [[skill-writing-voice]],
[[skill-fabric-licensing]], [[feedback-version-bump-revisions]].
