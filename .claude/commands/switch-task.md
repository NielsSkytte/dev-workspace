Switch (or set) the time-tracking task for the current **customer** project — lists that project's open/in-progress tasks so you can pick which one your time bills to. Task-level tracking is a customer-only detail; `own/…` and workspace (`Dev`) sessions don't use it.

Usage:
  /switch-task            ← list this project's tasks and pick one to track
  /switch-task [slug]     ← switch directly to a task by slug
  /switch-task off        ← stop task-level tracking (time bills to the project code)

## Scope

Resolve the current project from the session cwd. If it is **not** a `customers/<Client>/<Project>` path (i.e. an `own/…` or workspace/`Dev` session), tell the user task tracking isn't used there and stop — their time bills to the project's `fno_code` (or `INTERNAL-RND`) automatically. Do not create an `active-task` for non-customer projects.

## Instructions

1. **`off` / `none` / `clear`:** delete `C:\Dev\ops\time\active-task` and confirm time now bills to the project. Done.

2. **Gather this project's tasks:** read `ops/tasks/open/` and `ops/tasks/in-progress/` and keep the files whose `project:` frontmatter equals the current project. If there are none, say so and offer `/task` to create one; stop.

3. **Choose:**
   - If a `[slug]` arg was given and it matches one of them, select it.
   - Otherwise list them — one per line, `slug — title  (status · activity <activity>/task <fno_task>, or "no activity")` — and ask in plain text which to work on (accept a slug or the line number). **Do not use the AskUserQuestion tool** — the owner prefers open dialogue.

4. **Apply:**
   - Write the chosen slug to `C:\Dev\ops\time\active-task` (overwrite).
   - If the task was in `open/`, move it to `in-progress/`, set `status: in-progress`, and append a dated Log line (`YYYY-MM-DD — started (session task)`).
   - If the task's `activity:` is blank, prompt for it (one line) and write it into the frontmatter — F&O books time as Project ID → Activity → Task. If this project registers down to task level and `fno_task:` is blank, also prompt for the Azure DevOps work-item id; activity-only projects leave it blank.

5. **Confirm** in one line: `Tracking time to <slug> — <proj_id> · <activity> · <fno_task or "activity-level">.` Flag any missing `activity` so it gets filled before entry.

The time hook only tags a heartbeat with the active task when that task belongs to the session's project, so a slug set here (always this project's) is always valid, and a stale tag from another project drops itself. Keep this command mechanical and fast.
