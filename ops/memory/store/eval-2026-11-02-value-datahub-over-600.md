---
id: eval-2026-11-02-value-datahub-over-600
ts: 2026-11-02T13:00:00Z
type: evaluative
scope: project:customers/Carl-Ras/datahub
source: owner, /log 2026-11-02
tags: [value-model, adr-004, gut-check]
status: distilled
description: "Niels: datahub weighted/registered of 689-690% (W44, CarlRData-666/738) is excessive - gut says too high"
---

Owner, 2026-11-02, on the W44 hours table: "the two datahub seems excessive with over 600%".
Direction: weighted too HIGH.

Figures (hours.py last, W44): CarlRData-738 keyboard 4.62, measured 11.50, registered 4.00,
weighted 27.58 (690%); CarlRData-666 keyboard 0.60, measured 0.00, registered 0.75, weighted 5.17 (689%).

Facts behind it:
- The % divides by registered, which the re-split cut far below measured (738: 4.00 registered vs
  11.50 measured). Against measured, 738 is 240%.
- 666 has 0.00 measured but 5.17 weighted: weighted stayed where the hours were moved away from.
- Value records for 10-26..10-28 still carry CarlRData-555; the re-split moved registered hours
  but not the value records (open item in the 11-01 session log).
- 10-29 alone: 0.27 h keyboard -> 5.25 h weighted (19x).
Evidence for the ADR-004 re-evaluation.

Outcome 2026-11-02: partial moves (measure-moves.md `Hours` column) for 10-27 (1.75 h) and 10-28 (5.00 h) to process-insight. W44 after: 738 392%, 666 509%, process-insight 198% / 168%.
