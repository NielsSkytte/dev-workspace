---
id: eval-20261005-skill-description-budget
ts: 2026-10-05T12:00:00Z
type: evaluative
scope: workspace
source: session:ee830441
tags: [skills, descriptions, routing, opus-5-5]
status: distilled
description: "Skill review for Opus/Sonnet 5.5: no model-specific defects; the real gap was description length -- descriptions >= ~1,584 chars were cut in the listing and the last three alphabetically rendered empty (inference: shared budget)"
---

**Context (2026-10-05):** Q reviewed all 21 skills against the claude-api skill's prompt-audit and
model-migration guidance (report in session scratchpad). 14 minor, 7 rework; no hard-coded model
ids, no old-model workarounds.

**Observed:** in the session's skill listing, descriptions of 1,584+ chars were truncated (hand-offs
lost) and `writing-voice`, `time-tracking-to-fno`, `timestamp-timezone-pipelines` showed no
description. YAML was not the cause (all parse). Inference: a total budget for descriptions.

**Done:** fabric-project-access, fabric-deployment, fabric-warehouse-git, time-tracking-to-fno cut
to < 1,000 chars; fno-time-registration merged into time-tracking-to-fno and deleted. After the
cut, timestamp-timezone-pipelines rendered again in the same session.

**Rule going forward:** keep a skill description under ~1,000 chars; describe kinds of request,
not phrase lists; keep the sibling hand-offs. Calibrated urgency in descriptions is allowed (skills
under-trigger).
