---
id: eval-2026-11-18-gtm-prod-session
ts: 2026-11-18T19:50:00Z
type: evaluative
scope: customers/Carl-Ras/datahub
source: session:1a6805df
tags: [skill-eval, fabric-deployment]
status: distilled
description: "evaluative: fabric-deployment already described the per-stage model source trap, yet PROD Model_OneLake read TEST data for a week; Direct Lake viewer access was missing from the skill"
---

- fabric-deployment (references/powerbi-report-model.md section 4) named the per-stage OneLakeSourceUrl
  trap on 11-18, but nothing checked the second model, so PROD Model_OneLake stayed on TEST data until
  users reported empty visuals. The skill says "check after every model deploy"; it was applied to the
  model being worked on only. Gap: a check over all models in the target workspace.
- Direct Lake viewer access (SSO needs ReadAll; fix = fixed-identity connection) was not in any skill;
  added as section 4b. It surfaced only at go-live because Import never needed it.
- Self-inflicted: a Python edit of `.claude/commands/log.md` wrote `\b` as a backspace (path
  `C:\Dev\ops\bin`); found at the next /log and fixed. Write Windows paths in Python edits as raw strings.
- Session time was attributed to the wrong task for two days: an unclaimed /switch-task never took.
