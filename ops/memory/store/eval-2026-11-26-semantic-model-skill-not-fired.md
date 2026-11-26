---
id: eval-2026-11-26-semantic-model-skill-not-fired
ts: 2026-11-26T00:05:00Z
type: evaluative
scope: project:own/ProcessInsight
source: /log 2026-11-26
tags: [skills, semantic-model-authoring, powerbi-authoring, process-insight]
status: distilled
description: "Microsoft semantic-model-authoring skill (powerbi-authoring plugin) did not fire during PI model-generator work (tools/model.py, D43 rules); Niels expected it to fire automatically"
---

Niels, 2026-11-26: "i would have expected the fabric semantic modelling skill from MS to have fired automatically somehow." Context: 2026-11-25, generator rules for semantic models (base measures, role-playing dates, model check) built in Python that writes TMDL. The skill's trigger reads "before acting on a semantic model"; code that generates a model did not match it, so it was never loaded. The upstream SKILL.md was read once by URL for docs/research. Candidate fix: name the skill in own/ProcessInsight/CLAUDE.md for any change to tools/model.py, star.py, measures.py or model_check.py, so it loads by rule instead of by description match.
