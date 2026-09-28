---
id: eval-20260925-carlras-deploy-reversals
ts: 2026-09-25T18:30:00Z
type: evaluative
scope: project:customers/Carl-Ras/datahub
source: /log
tags: [evaluation, skills, fabric-warehouse-git, fabric-deployment, fact-only-language, capture-hook]
status: distilled
description: "Carl Ras deploy work 09-23..25: no skill is named in any daily record, and fabric-warehouse-git gained failure 8 from the work; four statements were reversed later in the stream (a wrong decimal type committed and pushed, a stale-items count, a root cause stated as found, an unproven 'someone added labels'), and the capture hook again stored command/skill bodies as the User field"
---

Trigger context: DEV->TEST->PROD deployment of Carl Ras Fabric-ETL, 2026-09-23 to 09-25, in
the datahub project.

- **Skills:** no skill name appears in the daily records for the three days. Whether
  `fabric-deployment` or `fabric-warehouse-git` fired is not recorded. The work produced a new
  failure mode in `fabric-warehouse-git` (failure 8, `cccfde6`), so the skill did not cover it
  beforehand.
- **Reversals (sentinel, 2026-09-28):** `InventoryOnHand` changed to `decimal(28,2)`, committed and
  pushed, then found wrong and reverted (`f0ca063`); "~10 items TEST never received" retracted
  after comparing definitions instead of commit dates; "the failures started from a change in
  Fabric's check" stated as a finding before it was labelled inference; "someone added labels
  by hand in DEV" stated as fact, later "cannot prove they ever existed". Each breaks
  `feedback-fact-only-language` or the compare-the-definitions habit.
- **Capture hook:** `/switch-task` and `/handoff` bodies, the claude-in-chrome skill body and
  task-notification payloads stored as the User field (8 records), plus 4 `pasted_content` tags.
  Same defect as 09-17 through 09-23; not fixed.

Rule for next time: compare item definitions, not git dates, before calling anything stale;
check a type change on a table file against the view's emitted type before committing it.
