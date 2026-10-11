---
id: eval-20261010-fabric-deployment-skill-not-used
ts: 2026-10-10T18:30:00Z
type: evaluative
scope: skill:fabric-deployment
source: /log
tags: [skill-eval, fabric-deployment, carl-ras]
status: distilled
description: "Carl Ras 10-10: diagnosing a PROD run that failed after a first deployment never loaded fabric-deployment, though it is that skill's exact trigger; two of its gaps (active value set, hand-set metadata tables) were also missing from the skill and tool"
---

- Context: PROD `PL_MainExecution` failing since the first TEST->PROD deploy. The fabric-deployment
  skill description names "first deploy into an empty or new workspace" and "VariableNotFound /
  BadRequest submit". The skill was not invoked; the session diagnosed from runs and repo files.
- New failure classes found that neither the skill nor `fabric_release.py` covered: the ACTIVE
  value set per workspace (not just the stage's set), and hand-set metadata tables
  (`marketo_columns` flags) that no seed rebuilds. The tool now covers both; the skill should gain them.
- The 09-25 deploy record already listed the two missing PROD connections; nothing tracked them
  to closure, so PROD ran 5 days red before anyone looked.
