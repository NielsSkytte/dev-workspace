---
id: feedback-time-attribution-dev-to-project
ts: 2026-06-22T15:50:00Z
type: semantic
scope: workspace
source: session:e642cd4e-5e1c-4a28-a96c-9d9f9a890aa7
tags: [feedback]
status: distilled
description: "Time attribution: project-rooted time always stays; Dev-rooted time clearly a project's gets reassigned to it (out of Dev only, never project-to-project)"
---

Attribution rule for the `ops/time/` time-tracking system: work done in a project (e.g. `marketo`) is **always** attributed to that project; `Dev`-rooted time that could be attributed to a specific project **should** be reassigned to that project rather than left as `Dev`/`INTERNAL-RND`. Only ever move time *out of* `Dev` into a project — never reassign between two named projects by judgement (that washes out).

**Why:** the original spec was pure cwd ("by session cwd, full stop"), but the hook attributes by the *launch* cwd. A session launched from `C:\Dev` but spent working on a project lands on `Dev` and under-bills the project (observed 2026-06-22: a `carl-ras/marketo` session recorded `cwd: C:\Dev` → heartbeats labelled `Dev`). The user wants project work credited to the project.

**How to apply:** best fix is to root sessions in the project folder (per-project VS Code Task) so cwd already names the project; otherwise reassign at the daily/weekly review gate by editing the timesheet. Encoded in `ops/time/README.md` §2 and `AGENTS.md` Time-tracking. Relates to the time-tracking system [[time-tracking-system]] and the still-blank `fno_code:` gap (customer projects read `UNSET` until coded).
