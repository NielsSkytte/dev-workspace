---
id: eval-2026-10-29-capture-encoding
ts: 2026-10-29T09:00:00Z
type: evaluative
scope: workspace
source: sentinel:/log 2026-10-29
tags: [memory, capture_turn, encoding, sentinel]
status: distilled
description: "capture_turn.py stores assistant text as UTF-8 decoded as cp1252 (mojibake like 'â–¶', 'Ã¦'); user lines are correct; harness markup (bash-input, pasted_content) lands verbatim in User lines"
---

Sentinel review of 2026-10-26..29 flagged 21 records with broken encoding in assistant bodies only
(2026-10-26.md:17 user "Vestforbrænding" vs :19 assistant "VestforbrÃ¦nding"); content intact. Four
User lines carried raw `bash-input`/`pasted_content` markup and emoji. Inference: the assistant text is
decoded with the console codepage in `.claude/hooks/capture_turn.py`. Fix worth doing there; distill
with characters repaired until then.
