---
id: workflow-large-return-timeout
ts: 2026-06-25T10:50:00Z
type: evaluative
scope: workspace
source: /log
tags: [workflow, tooling]
status: distilled
description: "Workflow synthesis returning two large files via schema hits a stream-idle timeout; files write to disk before the return so recoverable - prefer agent-Write or smaller returns"
---

Observed twice while building skills via the `Workflow` tool: a final **synthesis agent asked to
return two large files** (a SKILL.md + a references file) through a structured-output schema hit
`API Error: Stream idle timeout - partial response received`, and the workflow failed on
`out.skill_md` being null.

Mitigations that worked / to use next time:

- For large multi-file output, have the synthesis agent **Write the files directly** to disk and
  return only a short manifest, OR return **one** moderate file at a time, not several big ones via
  one schema.
- It is often **recoverable**: in the failing run the agent had already written both files to disk
  before timing out on the return, so the "failed" workflow still produced the artifacts - check the
  skill dir / output before re-running.
- Research-only workflows (agents return cited findings, the main loop authors the files) avoid the
  problem entirely and keep authorial control.

Not yet a skill edit - a `Workflow`-authoring habit. Tag for the next time a synthesis step returns
bulk content.
