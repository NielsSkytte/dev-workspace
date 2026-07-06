---
id: feedback-fact-only-language
ts: 2026-07-06T16:20:00Z
type: semantic
scope: workspace
source: session:8b788acf
tags: [feedback]
status: distilled
description: "NEVER imply - state facts only; label inference as inference; word choices must not suggest more than the evidence shows (e.g. 'leakage' implying data exfiltration)"
---

State facts; never imply. When something is an inference or a characterization, label it as such
explicitly. Word choices must not suggest more than the evidence supports.

**Why:** 2026-07-06 - the assistant described mixed-language model output written to a LOCAL file
as "Chinese token leakage". "Leakage" implied data leaving the machine; nothing left the machine.
Niels: "this exact type of language from you is what i hate the most." The same exchange included a
quality claim ("the model isn't working") resting on one data point, contradicting Niels's own
documented benchmark (sessions.md 2026-06-22 Session 3: qwen3:1.7b won on real turns) - claims
must be checked against recorded evidence before being asserted.

**How to apply:** all agents, all sessions. Before asserting a system defect: cite the record
(file + line). Before using a loaded word (leak, broken, dead, corrupt): does the evidence show
that, or something smaller? Prefer the smaller true statement.
