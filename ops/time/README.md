# Time tracking substrate

Tracks active working time **per project** (the level that has its own `CLAUDE.md` init):
`Dev` (this workspace setup itself), each `customers/<client>/<project>`, each `own/<project>`.
Optionally **per task** within a project (opt-in via `/task`). Time spent in `ops/` is not a
project of its own -- it rolls into `Dev`.

This is LLM-agnostic substrate (Guardrail 7). The Claude harness only *accelerates* it
(a hook appends heartbeats; `/time` and `/log` run the rollup). Everything below can be done
by hand by any LLM or by the user -- delete `.claude/` and nothing here is lost.

```
ops/time/
  README.md              <- this file: the spec + by-hand recipe (source of truth)
  rollup.py              <- accelerator that implements the algorithm below (tool-neutral python)
  active-task            <- present only while a task is "started"; holds one task slug (set by /task)
  heartbeats/            <- raw, append-only: one JSONL file per UTC date
    YYYY-MM-DD.jsonl
  timesheet/             <- rolled-up, reviewed output (the deliverable)
    YYYY-MM/             <- one folder per month (keeps the daily pile manageable)
      YYYY-MM-DD.md      <- a finalized day (local date); the unit of F&O entry
```

The split mirrors memory's `daily/` (raw) -> `store/` (curated): **heartbeats are immutable raw;
the timesheet is the reviewed truth.** You correct time by editing the timesheet, never the heartbeats.

**Not version-controlled.** `heartbeats/`, `timesheet/`, and `active-task` are gitignored — this is
operational output (regenerable from heartbeats), and a git history of hour-by-hour changes is noise.
The goal is the current per-day timesheet to enter into F&O, not a tracked archive. Only this `README.md`
and `rollup.py` (the system itself) are tracked. The data dirs are created at runtime by the hook and
`rollup.py` (`os.makedirs`), so they need not exist in a fresh clone.

## 1. Heartbeat (raw capture)

Every turn emits one heartbeat -- a JSON object appended as a line to `heartbeats/<utc-date>.jsonl`:

```json
{"ts_start":"2026-06-22T06:14:03Z","ts_end":"2026-06-22T06:51:20Z","project":"customers/Melbye/data-agent-offer","session":"abc12345","task":"2026-06-15-melbye-data-agent-offer"}
```

- `ts_start` -- when you sent the message (UTC, `...Z`). Captures "the time spent" on the turn.
- `ts_end` -- when the assistant finished the turn (UTC).
- `project` -- the session's project, derived from its working directory (see *Attribution*). `Dev` for any
  session not inside `customers/` or `own/` (workspace root, `ops/`, etc.).
- `session` -- session id (first 8 chars), for debugging only.
- `task` -- task slug if a task was "started" (`ops/time/active-task` present), else `null`.

Several heartbeats per turn are harmless: they are seconds apart and collapse into one stretch (below).

**By hand:** append a line per turn with the start/end times and the project of the folder you are in.

## 2. Attribution

**Default: by the session's working directory.** Whatever project the session is rooted in gets the
time, regardless of which files were touched. If you are in a Melbye session and edit a shared `Dev`
skill, that time bills to Melbye. The occasional cross-edit *between two real projects* is noise that
washes out; this keeps attribution predictable and free.

**One override -- `Dev` -> a project (never project -> project).** The workspace root (`Dev`) is the
catch-all, not a real billing target. When `Dev`-rooted time is *clearly* a single project's work --
e.g. the session was launched from the root but spent on Marketo -- attribute it to that project rather
than leaving it as `Dev`/`INTERNAL-RND`. This only ever moves time **out of** `Dev` into a project;
time already on a named project stays there, and time is never reassigned **between** two named projects
by judgement (that still washes out).

Because the hook attributes by the launch cwd, the surest way to get this right automatically is to
**root the session in the project folder** (per-project VS Code Task) -- then the cwd already names the
project. When a session was launched from the root instead, make the `Dev` -> project reassignment at
the daily review gate (section 5) by editing the timesheet.

**Task level (customer projects).** Within a `customers/<Client>/<Project>` a session's time can be
tagged to a **task**, which adds the F&O Activity/Task dimensions *beneath* the project id (see section 4).
The active task lives in `ops/time/active-task` (set by `/task start` or `/switch-task`, cleared by
`/task done|cancel` or `/switch-task off`). The hook only stamps a heartbeat with the active task when
**that task's `project:` matches the session's project** -- a stale or foreign tag left over from another
project's session never mis-bills. At the start of a customer session the project walk asks which of the
project's open/in-progress tasks this session is for. `own/…` and workspace (`Dev`) sessions have no task
level; they bill to the project id (or `INTERNAL-RND`).

## 3. Rollup: the 15+5 active-time model

A session can go stale for hours or days. We never count idle gaps. Per **(local date, project, task)**
group:

1. Take that group's heartbeats as intervals `[ts_start, ts_end]`, sorted by `ts_start`.
2. Walk them, merging into **stretches**: for each next interval, `gap = next.ts_start - current.end`.
   - `gap <= 15 min` -> same stretch; extend `current.end = max(current.end, next.ts_end)`.
   - `gap  > 15 min` -> close the stretch, start a new one. (The idle gap is discarded -- this is what
     makes a session that was stale for days cost nothing.)
3. Each stretch = `(end - start) + 5 min` tail buffer (reading/thinking after the last reply). A lone
   turn = its own duration + 5 min.
4. Group hours = sum of stretch durations, **rounded to the nearest 0.25 h** (`round(h*4)/4`), then
   **floored to a 0.5 h minimum**: any logged work on an F&O line that day (a decision, a file created or
   edited, anything) counts as at least 0.5 h.

Constants: idle timeout **15 min**, tail buffer **5 min**, rounding **0.25 h**, minimum **0.5 h**.
Bucketing is by **local time** (the machine's timezone), while heartbeats are stored in UTC.

Known edge: bouncing between two projects inside 15 min can let one project's stretch span the other's
detour (slight overcount); and a stretch crossing local midnight is split into two (two buffers). Both
are rare and small -- the daily review gate (below) is where you fix anything that looks wrong.

## 4. F&O dimensions

A Dynamics F&O time line is **Project ID -> Activity -> Task** (the Task dimension is fed from the
Azure DevOps work item). Project ID always applies; Activity and Task are optional sub-dimensions
*under* it -- some projects register only at activity level, some down to task, one or many of each.
Resolution is **additive** (a task adds its activity/task beneath the project id; it does not replace it):

1. **Project ID** -- the project's `CLAUDE.md` `## Identity` `fno_code:` field. `Dev` -> `INTERNAL-RND`
   (internal R&D; non-billable). Missing -> `UNSET` (surfaced so you add it).
2. **Activity** -- the tagged task's `activity:` field (blank if untagged or activity not set).
3. **Task** -- the tagged task's `fno_task:` field = the linked Azure DevOps work-item id (blank for
   activity-only projects).

**Grouping is by the finest dimension present** (README's guiding rule): rows sharing the full
`(project id, activity, task)` key merge; a task-level line is never rolled up into its activity, an
activity-level line merges only when there is no task, and project-level only when there is no activity.
**Billable** = the project is a `customers/…` project (`Dev` and `own/…` are non-billable).

## 5. Daily review gate + cadence

Heartbeats accrue continuously; a day becomes **final** when its timesheet is written and you have
reviewed/adjusted it -- this happens at `/log` (end of day). The rollup:

- **Finalizes** every *complete* past day that has heartbeats but no `timesheet/<YYYY-MM>/<date>.md` yet
  (**catch-up** for missed days).
- Today is only ever **previewed** (live running tally), never auto-finalized, since it is still accruing.

There is no weekly aggregate file: F&O entry is per day, so a date-dropped weekly rollup adds nothing.
Pull a whole week or month with the by-date report modes below.

`rollup.py` modes:
- `python ops/time/rollup.py` -- finalize missed complete days. Use at `/log`.
- `python ops/time/rollup.py --preview` -- print today's live tally; writes nothing. Use at `/time`.
- `python ops/time/rollup.py --week [YYYY-Www]` -- print a **by-date** report for one ISO week (default: current); writes nothing.
- `python ops/time/rollup.py --month [YYYY-MM]` -- print a **by-date** report for one month (default: current); writes nothing.
- add `--merge` to either -- **consolidate** small entries (see below); still by date.

The `--week`/`--month` reports are **by date** (one row per date/project/task) because time is
entered into F&O per date. They read the finalized `timesheet/<YYYY-MM>/<date>.md` files -- so any manual
corrections are honoured -- and fall back to live heartbeats for a date not yet finalized (marked
`live`). Use them to pull a week or a month at entry time. They derive only; they never write.

**Consolidation (`--merge`)** avoids a scatter of tiny entries. Any day-entry **>= 2 h** stays exactly
where it is. For every F&O line (project id + activity + task), its **< 2 h** day-entries within an ISO
week are **summed and placed on a single day of that week**, chosen so that day's total never exceeds
**9 h**. The merged entry prefers a day that line was actually worked. Days already over 9 h purely from
untouched >= 2 h entries are flagged, not redistributed. Monthly/weekly totals are unchanged -- only the
spread across days changes. `/time` runs the reports with `--merge` on by default; pass `raw` to see
every entry.

**By hand:** for each unfinalized day, run the model in section 3 per group, write the table to
`timesheet/<YYYY-MM>/<date>.md`, eyeball it, adjust if a number is obviously off.

## 6. Timesheet (the export)

`timesheet/<YYYY-MM>/<date>.md` -- a table with columns **Project | Proj ID | Activity | Task | Hours |
Billable**, one row per F&O line (project id + activity + task), hours rounded to 0.25 h (min 0.5 h),
with billable vs internal totals. Copy the rows straight into F&O time entry (Project ID -> Activity ->
Task -> hours).

**The daily file is the unit of F&O entry** -- time is entered per date. The `--week`/`--month` report
modes (section 5) are just the daily files stacked into one by-date view for a week or a month, so you
can pull a whole period at once without a separate aggregate file.
