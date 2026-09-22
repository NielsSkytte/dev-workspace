---
id: eval-20260922-today-page-ask-text
ts: 2026-09-22T09:30:00Z
type: evaluative
scope: workspace
source: /log
tags: [evaluation, ui-text, dashboard, today, feedback, internal-tooling]
status: distilled
description: "The Today page's Unsent asks rows showed the task Progress note instead of the ask; the owner read the texts as unintelligible. No skill fired - feedback-explanatory-ui-text-flat-manual-register was written about customer-facing tool text and was not applied to Niels's own tools, where the same rule holds"
---

What happened: the owner opened Today and said he did not understand the texts under
"Unsent asks", and that too many were being generated. Two separate defects. The row body
rendered `task.now` -- the Progress note, which is about the work, not about the ask -- so the
line beside "Unsent asks" never said what the ask was. Separately the hint read "the task says
the customer needs to be asked and it has not gone out", a connective sentence where a labelled
statement was wanted.

Skill observation: no skill fired, and one should have applied. The stored preference
`feedback-explanatory-ui-text-flat-manual-register` is scoped in its own text to "explanatory
text that a customer reads inside a tool". It was written from the DataCompare app card, but the
rule is not about the reader being a customer -- it is about text that sits inside a tool.
Niels's own dashboards are in scope. The Today page shipped with narrative hints and a tile
foot ("waiting on you to send") that stated a feeling rather than the condition
(`customer_ask: open`).

Rule for next time: when a page lists items selected by a field, the row must show that field's
own content, and the hint must name the condition that put the row there. Applies to internal
pages, not only customer-facing ones.

Second finding, unresolved: the ask count is coarse. `customer_ask` is one flag per task, so a
task holding three separate asks counts once, and an ask on a task that is not in progress (or
is parked waiting on the same customer) still demands attention today. The owner chose a
per-ask drop action over a filter for now.
