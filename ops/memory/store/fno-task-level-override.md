---
id: fno-task-level-override
ts: 2026-10-05T10:00:00Z
type: semantic
scope: workspace
source: /log
tags: [time, fno, rollup, attribution, carl-ras]
status: distilled
description: "A work-task can carry its own fno_code / fno_category: the rollup puts that Proj ID on the line, the customer's fno_requires stops applying, and the Time page shows Kategori; first use Carl Ras Dataverse write-back -> 230-04 / 112744 / F (2026-10-05)"
---

- Before 2026-10-05 the Proj ID came only from the project's `fno_code`; a task could not move a line
  to another F&O project.
- Now: `rollup.line_proj_id(project, slug)` = task `fno_code` or project `fno_code` (rollup + value.py);
  `fno.task_overrides()` finds the task again from the line's `proj_id|activity|fno_task`; such a line
  is exempt from the customer's `fno_requires` (fno.missing, attribution.drift) and shows no sheet
  conflict; `fno_category:` shows as "Kategori X" on the Time page and in the export's Category column.
- Days finalized before the override keep their old Proj ID; September's Dataverse lines stay on
  230-02 / CarlRData-557 (posted journals).