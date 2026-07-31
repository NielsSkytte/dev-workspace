---
id: eval-2026-07-31-skills-available-not-firing
ts: 2026-07-31T08:10:00Z
type: evaluative
scope: workspace
source: session:04e254a5
tags: [evaluative, skills, fabric-project-access, pingala-fabric-platform, hooks-subdir-session-gap, memory-summarizer, fact-only-language]
description: "evaluative: at Dev root the workspace skills ARE loaded (the listing reflected a live edit) and still did not fire on Link-to-Fabric/Dataverse questions - narrows the 07-30 cascade-vs-trigger question to trigger-miss at workspace level; local summarizer turned labelled inference into a fact"
status: distilled
---

Session 04e254a5, 2026-07-31, rooted at `C:\Dev` (workspace root). Follow-on to
`eval-2026-07-30-env-discovery`, which left two undistinguished causes for workspace skills never
firing: (1) the skills directory does not cascade to the session, or (2) the triggers miss.

## The 07-30 question, narrowed

**At workspace root the skills are demonstrably present and still do not fire.** Direct evidence
they were loaded: the available-skills listing named `fabric-project-access`, and when its
frontmatter description was edited mid-session the listing **re-emitted with the new text**. So
availability is not the failure mode here.

Across this session the subjects were "Link to Fabric", "Dataverse environments", "Fabric
workspace", "Azure Synapse Link" — `pingala-fabric-platform` names *Dataverse integration* and
*Link to Fabric* in its own trigger list, and `fabric-project-access` names Dataverse "Link to
Microsoft Fabric". Neither fired. Both were edited by hand instead.

- **Supported:** at workspace root, cause (2) — trigger miss.
- **Still untested:** the project-rooted leg. `eval-2026-07-30` was a project-rooted session, so
  cause (1) is not ruled out *there*. The cheap test named on 07-30 has still not been run.
- **Consequence if this holds:** description tuning is the right lever at workspace level, and the
  edits made this session (adding operational phrasings like "which environment has the Link to
  Fabric", "can two Dataverse environments share one Fabric workspace") are a live experiment —
  check next session whether the skill fires unprompted on one of them.

## Own-process observation

The Link-to-Fabric question was answered by going straight to MS Learn without first checking
whether a workspace skill already covered it. That is the same failure the skill listing is meant
to prevent, from the operator side rather than the harness side. The answer was correct, but the
skill would have been the cheaper first stop — and the gap it revealed is exactly what got written
back into section 0.

## Memory-pipeline observation — the local summarizer stated inference as fact

`daily/2026-07-31.md`, record `20260731T074132Z-04e254a5`, summarized the Link-to-Fabric answer as
"the system allows for multiple lakehouses in one workspace". The turn it summarizes explicitly
labelled that as **inference from an absence in the documentation** and refused to assert it. The
summarizer stripped the hedge and produced a bare claim.

This is a `feedback-fact-only-language` violation manufactured *by the pipeline*, not by the
assistant, and the deterministic sanitizer cannot catch it — charset, injection markers and bounds
all pass. It is precisely the class `sentinel` exists for. **Flagged, not distilled.**

Second, milder flag in the same file: record `20260731T073314Z-04e254a5` says the `own/` repo was
"left untouched" in a turn that committed `277e949` to it.

`sentinel` was again not dispatched — the standing no-subagents instruction applies to this session
too (5th consecutive `/log`). Daily file hand-vetted per `ops/memory/README.md` > Output
validation: charset clean, no injection markers, all records in bounds, two fidelity flags above.
