---
id: eval-20260929-fno-registration-skill-browser-close
ts: 2026-09-29T14:00:00Z
type: evaluative
scope: workspace
source: session:a110c294
tags: [skill, fno-time-registration, fno, browser, evaluation]
status: distilled
description: "September F&O close run on the fno-time-registration skill + /fno, via the browser fallback on the owner's instruction: pre-flight and Rule 0 caught five bad ids before a line went in; one stale-coordinate click still hit Tilbagefoer (cancelled); element-reference clicks and read-back of every field held; 'approved stays unposted' did not hold"
---

**Trigger.** Owner: "register the september hours per week per company ... take control of my
browser". The `/fno` sequence and `fno-time-registration` skill were followed; the Excel add-in path
was never tried -- the owner asked for the browser, which the skill allows only as a fallback.

**Helped.**
- **Rule 0 / pre-flight** stopped entry on five ids that would have failed or mis-billed: Aeven
  `4058-1` (does not exist; 4058 in PDK4), CarlRData-557 and -666 (not in F&O), Matas 65904 and 72114
  (DevOps items without F&O fields). New method, now in the skill: read
  `/data/DevOpsIntegrationV2_PIN` from the F&O session -- a usable task has `CustomTaskId` and
  `CustomProjectId`.
- **Read back every field after typing** (a script over the row's inputs, including `Rolle-id` and
  `aria-invalid` on Opgave) caught nothing wrong in 44 lines -- and showed that `Timer` pre-fills from
  the task (10,50 / 14,25), so it must always be typed.
- **Element-reference clicks** (`find` refs, and focusing fields by aria-label) replaced coordinates
  after the one miss; no further misclicks.

**Did not help / should have fired.**
- **Stale coordinates recurred once:** the toolbar shifted between screenshot and click and
  `Tilbagefoer` opened its copy/reverse dialog; cancelled before it ran. The skill's rule
  ("re-screenshot before every click") was followed and was not enough -- the layout moved after the
  screenshot. Prefer element references outright for toolbar buttons.
- **"Approved stays under Ikke bogfoert" is not a resting state here.** All six approved journals were
  posted by someone else within hours, which made a planned re-layout impossible. The skill should say:
  make every correction before approving.
- **The day cap was not part of the entry checks.** Scaled rows reached 24,25 h on one date and the
  manual spread aimed at ~12 h; the owner's rule is 7,5 / 9 per customer. Now encoded in the page
  (`packDays`); the skill does not mention it yet.
- The browser was the bottleneck again: screenshots timed out, the window shrank, the extension
  dropped once and F&O asked for sign-in mid-run.
