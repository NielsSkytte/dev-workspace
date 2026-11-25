---
id: carlras-prep-for-ai-lsdl-custominstructions
ts: 2026-11-25T20:40:00Z
type: semantic
scope: project:customers/Carl-Ras/dataagent
source: session b05a9093 2026-11-25
tags: [fabric, data-agent, prep-for-ai, carl-ras]
status: distilled
description: "Prep for AI AI instructions are stored as CustomInstructions in definition/cultures/<culture>.tmdl linguisticMetadata JSON; the file only appears after Prep for AI is set once; replacing that one value round-trips byte-identical"
---

First committed from the service 2026-11-25 (Semantic-Model 6e3da48): cultures/en-US.tmdl, 144,707 lines, mostly generated Q&A terms; CustomInstructions is the last key. AI data schema had not been set: the dialog showed the default (hidden fields excluded) and the definition had no culture part before. Writing via git + updateFromGit + model refresh worked (PR 4). REST-written CustomInstructions on a model without a culture file was accepted by the service (Pingala demo, factory v0.2) but the agent had not used the rule after 10 min (Direct Lake syncs Prep for AI at most daily; unproven).
