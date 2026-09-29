---
id: matas-fno-task-split-65904-65905
ts: 2026-09-08T12:40:00Z
type: semantic
scope: project:customers/Matas/DataCompare
source: /log
tags: [project, matas, time, fno, billing, task, activity]
status: distilled
description: "Matas DataCompare books to F&O project 212-01 with activity 111953 on every line; the task splits the work: Task-65904 = the compare engine and the app (the delivery), Task-65905 = the configuration work (Link to Fabric, access, setup). Recorded in the project's CLAUDE.md so a session does not have to ask. An earlier note claiming 65904 was never created was wrong. From 2026-09-15 all Matas work books to Task-72114 (PoC approved 2026-09-14); 65904 covers work up to and including 2026-09-14"
---

**Why it matters beyond a label.** Time was defaulting to the only open task on the project
(2026-07-06-matas-enhance-user-stories, which carries 65905), so engine and app days were booking to
the configuration task. The F&O line is identical either way - same project, same activity - but the
internal register then says the wrong thing, and a customer asking what was done on a date gets the
wrong answer.

Corrected on 2026-09-08: 2026-09-07 and 2026-09-08 moved to 65904, the reclaim ledger moved to 65904,
and a task 2026-09-08-matas-datacompare-engine-app now carries the engine and app work.

**2026-09-21 (check-in, owner): a third task.** The PoC was approved on 2026-09-14. All Matas work
after 2026-09-14 books to **Task-72114** (same project and activity); work up to and including
2026-09-14, and all reclaim, books to 65904. The cutover at the 14th is the assistant's reading of
two overlapping owner statements ("all work this month and the reclaim on 65904", "all work after
the 14th on 72114"), which the owner accepted without correction. Task file:
`2026-09-21-matas-datacompare-production`. Reclaim had to sit before 2026-09-10, the first PoC demo:
between that demo and the approval no development time was allowed.

**2026-09-29 (owner): Task-72114 books to activity 110383 (consultant), not 111953.** F&O derives it from the task once the DevOps work item carries project 212-01 and the activity; verified on a journal line. Task-65904 stays on 111953.
