Manage the workspace task store — the cross-project queue of business work in flight. This is the **Output** stage of ICOR (the inbox `/todo` is Input; promoting an item here is the Control step). See `ops/tasks/README.md`.

Usage:
  /task [description]          ← create a new task (you structure it from context)
  /task                        ← list open + in-progress work
  /task start  [slug]          ← move a task open → in-progress
  /task done   [slug]          ← move a task → done (record the outcome)
  /task cancel [slug]          ← move a task → cancelled (record why)

The store lives at `C:\Dev\ops\tasks\` with subfolders `open/`, `in-progress/`, `done/`, `cancelled/`. State is the folder; the task file is the record.

## Instructions

### `/task` with no arguments — list

Read `open/` and `in-progress/`. Show them grouped by status, most recent first, one line each: `slug — title  (project, owner)`. Keep it tight. Don't list done/cancelled unless asked.

### `/task <description>` — create

This is the Control step: the user gives raw intent; **you** add the structure. Do NOT run a rigid interview.

1. From the description **and the current conversation/project context**, infer: `title`, `project` (which DEV project it relates to, or blank for workspace-level), `owner` (route it — `fabric-back`/`semantic`/`fabric-front`/`content`/`architect`/`Q`/`self`; default `M` to route later if unclear), `priority`, and a one-line **Why**. Only ask the user if something material is genuinely ambiguous — otherwise fill sensible values and let them correct.
   - **If `project` resolves to a customer with no `customers/<Customer>/` folder, scaffold a placeholder project first** (per AGENTS.md > Conventions: "A referenced customer always has a project"), then point `project` at it. Don't run the full `/new-project` interview mid-triage — create the stub and flag it.
   - **F&O dimensions (customer tasks only).** F&O books time as Project ID → Activity → Task, where Project ID comes from the project's `CLAUDE.md` and the task adds the sub-dimensions beneath it. If `project` is a `customers/...` project, capture `activity` (the F&O activity/WBS this task rolls under) and, for projects that register down to task level, `fno_task` (the linked Azure DevOps work-item id). Ask in one line if not evident (`"F&O activity for this task? And a DevOps task id, or is activity-level enough?"`). Some projects use only an activity; leave `fno_task` blank then. For `own/…` or workspace-level tasks leave both blank — task-level detail is customer-only (those bill to the project id or `INTERNAL-RND`).
2. Create `tasks/open/YYYY-MM-DD-<slug>.md` from `_TEMPLATE.md` with those fields (including `activity`/`fno_task` for customer tasks) and today's `created` date. Put the work in the user's own words under **What**.
3. If the task originated from a captured line, check that line off (`[x]`) in its source file and record where it came from: a `ops/TODO.md` capture → mark the line `[x]`, append `→ promoted to task \`tasks/open/<file>.md\``, and set `source: todo`; a project `INBOX.md` line → set `source: inbox`. Otherwise `source: direct`.
4. Confirm in one or two lines: the slug, title, and how you routed it (project/owner). Note any field you guessed so the user can correct.

### `/task start|done|cancel <slug>` — transition

1. Find the task file by slug across the subfolders.
2. Move it to the target folder (`in-progress/`, `done/`, or `cancelled/`) and update `status` in the frontmatter.
3. Append a dated line to the **Log** — for `done`, the outcome; for `cancel`, the reason.
4. **Time tagging (task-level tracking):** on `start`, write the slug to `C:\Dev\ops\time\active-task` (overwrite) so heartbeats bill to this task until it changes; on `done`/`cancel`, delete that file if it holds this slug. The time hook only tags a heartbeat with the active task when that task's `project:` matches the session's project, so a foreign tag never mis-bills. For picking among several tasks of the *same* customer project mid-session, use `/switch-task`. See `AGENTS.md` > Time tracking.
5. Confirm in one line.

Keep this command mechanical and fast. Routing judgment happens at create; everything else is bookkeeping.
