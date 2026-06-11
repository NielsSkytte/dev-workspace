Manage the workspace task store — the cross-project queue of business work in flight. This is the **Output** stage of ICOR (the inbox `/park` is Input; promoting an item here is the Control step). See `.claude/tasks/README.md`.

Usage:
  /task [description]          ← create a new task (you structure it from context)
  /task                        ← list open + in-progress work
  /task start  [slug]          ← move a task open → in-progress
  /task done   [slug]          ← move a task → done (record the outcome)
  /task cancel [slug]          ← move a task → cancelled (record why)

The store lives at `C:\Dev\.claude\tasks\` with subfolders `open/`, `in-progress/`, `done/`, `cancelled/`. State is the folder; the task file is the record.

## Instructions

### `/task` with no arguments — list

Read `open/` and `in-progress/`. Show them grouped by status, most recent first, one line each: `slug — title  (project, owner)`. Keep it tight. Don't list done/cancelled unless asked.

### `/task <description>` — create

This is the Control step: the user gives raw intent; **you** add the structure. Do NOT run a rigid interview.

1. From the description **and the current conversation/project context**, infer: `title`, `project` (which DEV project it relates to, or blank for workspace-level), `owner` (route it — `fabric`/`content`/`architect`/`Q`/`self`; default `M` to route later if unclear), `priority`, and a one-line **Why**. Only ask the user if something material is genuinely ambiguous — otherwise fill sensible values and let them correct.
2. Create `tasks/open/YYYY-MM-DD-<slug>.md` from `_TEMPLATE.md` with those fields and today's `created` date. Put the work in the user's own words under **What**.
3. If the task originated from an inbox line, check that line off (`[x]`) in `.claude/INBOX.md` and set `source: inbox`.
4. Confirm in one or two lines: the slug, title, and how you routed it (project/owner). Note any field you guessed so the user can correct.

### `/task start|done|cancel <slug>` — transition

1. Find the task file by slug across the subfolders.
2. Move it to the target folder (`in-progress/`, `done/`, or `cancelled/`) and update `status` in the frontmatter.
3. Append a dated line to the **Log** — for `done`, the outcome; for `cancel`, the reason.
4. Confirm in one line.

Keep this command mechanical and fast. Routing judgment happens at create; everything else is bookkeeping.
