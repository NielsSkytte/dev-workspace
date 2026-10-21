---
id: feedback-copenhagen-time
ts: 2026-10-22T00:10:00+02:00
type: feedback
scope: workspace
source: conversation
tags: [time, timezone, reporting]
status: distilled
description: "Niels 2026-10-22: state times to him in Copenhagen time (CET/CEST), not UTC; UTC is only how Fabric runs report"
---

- Niels (2026-10-22): "im almost always on copenhagen time, so while utc is how the runs go, its not my/our time."
- Rule: every time told to Niels (run starts and ends, schedules, ETAs) is given in Copenhagen local time
  (Europe/Copenhagen: CEST UTC+2 in summer, CET UTC+1 from the last Sunday of October). Convert Fabric's UTC
  timestamps before reporting. Only quote UTC when it matters, and then label it.
- Trigger: a run was reported as "started 21:34 UTC" when it was 23:34 in Copenhagen.
