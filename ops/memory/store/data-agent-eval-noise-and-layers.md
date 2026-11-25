---
id: data-agent-eval-noise-and-layers
ts: 2026-11-25T20:40:00Z
type: semantic
scope: project:customers/Carl-Ras/dataagent
source: session b05a9093 2026-11-25
tags: [fabric, data-agent, evaluation]
status: distilled
description: "Fabric data agent eval: identical config varies by about 3 of 34 run to run; compare layers on 3-run means with a 10 min settle after deploy; on Carl Ras the agent instructions gave the lift, Prep for AI almost none on well-named measures"
---

Carl Ras 2026-11-25, generated test set (DAX against Model_OneLake). 34 q: A bare 26/26/26, B +Prep for AI 27/26/26, C +agent instructions 32/32/33 (smoke 34, first C 31). 52 q: B 36/41/40, C 50/49/49. Agent table deselection did not stop out-of-scope answers (layer A answered stock and GL questions); only agent instructions did. Failures in C were mostly empty results or could-not-fetch answers, not wrong measures.
