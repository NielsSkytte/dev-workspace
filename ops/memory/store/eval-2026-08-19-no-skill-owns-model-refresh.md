---
id: eval-2026-08-19-no-skill-owns-model-refresh
ts: 2026-08-19T10:30:00Z
type: evaluative
scope: workspace
source: session:3582ea00-1223-4496-8acc-d74e4a5b233d
tags: [evaluation, skills, roster, semantic-model]
status: distilled
description: "Eighth consecutive session with no Fabric skill firing - and this time none should have: no skill owns semantic-model refresh failure, and the roster member that does is an agent a standing instruction blocks"
---

## The checkpoint answer

**Did a skill fire?** No. **Should one have?** No existing one — and that is the finding.

The whole session was a semantic-model refresh failure: an Analysis Services error code, a TMDL
column type, an Import partition, a refresh history. Nothing in the skill set covers it.
`fabric-deployment` owns promotion mechanics, `fabric-warehouse-git` the warehouse-as-code
contract, `pingala-fabric-platform` the architecture; the closest trigger is that skill's
"Power BI semantic models", which is an architecture bullet, not diagnosis.

**The capability exists as an agent, not a skill.** The `semantic` agent's definition names
"refresh and processing issues" outright — and the session ran under a standing
*no-subagents-unless-asked* instruction, so it was never dispatched. Eighth consecutive session
with the Fabric skills silent, but the first where the gap is structural rather than a trigger
miss.

## What this suggests

Diagnostic knowledge that is reached for *while debugging* wants to be a skill (auto-fires on the
error string); role knowledge wants to be an agent. `0xC112001A`, `ModelRefresh_ShortMessage_
ProcessingError`, "Value was either too large or too small for a Currency", and the
Fixed-Decimal-is-Currency ceiling are all verbatim triggers a skill could carry — the same shape
as `fabric-deployment`'s error-string list, which is the one thing in this workspace that has
demonstrably worked when invoked.

Not proposing the skill here; recording that the gap is real, and that the workaround used
(hand-enumerating the model's typed columns and measuring them) is exactly the procedure such a
skill would hold.

## Related

- `carlras-currency-ceiling-one-row` — the knowledge that would go in it.
- `eval-2026-08-18-skills-silent-sixth`, `eval-2026-08-14-skill-verbatim-trigger-miss` — the
  trigger-miss series this one is *not* a continuation of.
