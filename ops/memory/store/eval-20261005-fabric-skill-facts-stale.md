---
id: eval-20261005-fabric-skill-facts-stale
ts: 2026-10-05T12:00:00Z
type: evaluative
scope: workspace
source: session:ee830441
tags: [fabric-data-agent, fabric-licensing, fabric-pipeline-notebook, timestamp-timezone-pipelines, staleness]
status: distilled
description: "Re-verification 2026-10-05 found Fabric skills materially stale: Assistants API retired 2026-08-26 (skills said 'shuts down'), SDK pin 0.1.25a0 broken for eval, 12 licensing corrections, Spark start 5-10 s not 3-5 min, watermark SQL had 3 bugs"
---

**Context:** bullet 3 of the 5.5 skill review; fabric-back agent verified every flagged fact on MS
Learn and stamped `verified 2026-10-05`.

**What was wrong:** Assistants API retired 2026-08-26 (now MCP endpoint or `FabricOpenAIResponses`);
`evaluate_data_agent` defaults to the Assistants path up to 0.1.31a0 -> pin 0.1.32a0; Foundry Fabric
tool has no SPN support; admin settings renamed/moved; F SKUs to F8192; starter pool 5-10 s; SQL
endpoint allows views/procs; AT TIME ZONE works; timestamp skill's watermark SQL wrong across DST.

**Open:** `fabric-data-agent-testing` few-shot example -- agent says `evaluate_few_shot_examples`
does not exist (public method `datasource.evaluate_few_shots()`), skill line 171 asserts the
opposite; settle with a run in a Fabric notebook.

**Lesson:** fabric-licensing's own quarterly re-verify rule lapsed silently (102 days); dated
stamps without a routine that reads them do not prevent staleness.
