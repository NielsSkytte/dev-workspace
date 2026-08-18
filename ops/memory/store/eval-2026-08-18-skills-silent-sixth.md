---
id: eval-2026-08-18-skills-silent-sixth
ts: 2026-08-18T18:45:00Z
type: evaluative
scope: workspace
source: session:metaatomic-fabric-host
tags: [evaluative, skills, fabric-deployment, fabric-pipeline-notebook, pingala-fabric-platform, skills-fabric-deployment-late-trigger]
status: distilled
description: "evaluative: sixth consecutive session with Fabric skills silent - two days of notebook deployment, lakehouse writes and Fabric REST work, and none of the three matching skills fired"
---

Two sessions of nothing but Fabric work: deploying a notebook through the Items API, running it
through the Job Scheduler API, uploading to OneLake, reading SQL analytics endpoints, workspace
identity, notebook kernels. **No skill fired.**

Candidates that describe this work:

- `fabric-pipeline-notebook` — "designing and debugging Microsoft Fabric pipelines that orchestrate
  notebooks … notebook behaviour that differs between interactive and pipeline-triggered runs".
  That last clause is *precisely* the identity question that took two rounds to get right.
- `fabric-deployment` — "whenever an item moves DEV → TEST → PROD", "is this item portable", item
  ownership / LastModifiedBy / takeover. We deployed an item and spent a full exchange on which
  identity owns its execution.
- `pingala-fabric-platform` — "our Fabric setup", workspace structure, Atomic. The whole session was
  about running our tooling inside an Atomic customer's workspace.

Sixth consecutive session. `eval-2026-08-14-skill-verbatim-trigger-miss` established that even a
**verbatim substring** of a skill's own trigger list does not fire it, which ruled out description
quality. This session adds nothing new about the cause and everything about the cost.

## The cost this time is measurable

`fabric-pipeline-notebook` exists because notebook-vs-pipeline execution differences are a known
trap. I answered the identity question wrong
([[eval-2026-08-18-answered-a-narrower-question]]) and shipped a token-hook defect to a customer's
workspace. A skill that fired on "notebook" + "pipeline" + "identity" is exactly the intervention
that was missing, and it is one of the three that stayed quiet.

## What did work

Nothing from the skill layer. What caught the problems was **running the thing for real**: a fresh
clone found the silent semantic-model gap, a notebook kernel found `BrokenProcessPool`, a lakehouse
output path found the project-name defect, a second run found the frozen provenance strip. Four
defects, four real executions, zero found by review or by a skill.

**Standing conclusion, now six sessions old:** treat the Fabric skills as documentation to be read
deliberately, not as something that will arrive when relevant. If the roster is meant to intervene,
the trigger mechanism needs fixing — not the descriptions.

Related: [[eval-2026-08-14-skill-verbatim-trigger-miss]], [[skills-fabric-deployment-late-trigger]],
[[eval-2026-07-31-skills-available-not-firing]]
