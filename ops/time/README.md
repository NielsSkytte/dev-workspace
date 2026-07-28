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
- `project` -- derived from the session's working directory (see *Attribution*): any depth inside a
  project maps to `customers/<client>/<project>` or `own/<project>`; a customer node itself maps to
  `customers/<client>`; anything else under `C:\Dev` is `Dev`. Sessions outside `C:\Dev` emit no heartbeat.
- `session` -- session id (first 8 chars), for debugging only.
- `task` -- task slug if a task was "started" (`ops/time/active-task` present), else `null`.

Several heartbeats per turn are harmless: they are seconds apart and collapse into one stretch (below).

**By hand:** append a line per turn with the start/end times and the project of the folder you are in.

## 2. Attribution

**The active task decides; the working directory is the fallback.** (Reversed 2026-07-28 — see
ADR-003. Before that, cwd decided and a task that disagreed was discarded.) The reason: a project
routinely spans **several repos** and a repo hosts **several tasks**, so the folder cannot express
which work is in play. Carl Ras showed both at once — one Datahub project across `Landingzone-ETL`
and `Fabric-ETL`, and `Fabric-ETL` alone holding the GTM ingest, the capacity scale-up and
CapacityManager.

Resolution order, per turn:

1. If an active task is set **and** it passes the guards below -> its `project:` is the project, and
   the heartbeat carries the task tag.
2. Otherwise -> the session's working directory (rules below), with no task tag.

**Two guards, both load-bearing:**

- **Same customer only.** A task may override cwd only within the same customer; a customer node
  (`customers/<Client>`) is overridden by a task on one of its projects, which is how node-level
  `UNSET` time resolves itself. **`Dev` and `own/…` are never overridden** — moving workspace time
  onto a customer is the direction that over-bills, so it stays a deliberate call at the review gate
  (the `Dev` -> project override below).
- **Per-session marker.** `active-task` holds one entry **per session**:
  `{"sessions": {"<session-id>": {"slug", "set_at"}, …}, "unclaimed": {"slug", "set_at"} | null}`.
  A session reads only its **own** entry, so a tag set in another session — forgotten from Monday,
  or running concurrently in another window — never applies here. The slash commands cannot know
  the session id, so they write to `unclaimed`; the next turn adopts it, but **only if the task
  passes the same-customer test**, which stops a concurrent session on another customer from
  taking it. Entries older than 7 days are pruned on write. Two older formats are still read: the
  single record `{slug, session, set_at}` and a bare slug on one line — both land in `unclaimed`.
  **Write it with the merge-safe helper in `/switch-task`, never by overwriting the file**, or you
  will wipe the other open sessions' entries.

Within a project, whatever files you touch is irrelevant — attribution follows the session, not the
edits. If you are in a Melbye session and edit a shared `Dev` skill, that time bills to Melbye. The
occasional cross-edit *between two real projects* is noise that washes out.

**Setting the task is not a ritual you must remember.** A `SessionStart` hook
(`.claude/hooks/session_task.py`) resolves it for you: exactly one open task on the project -> it is
set automatically; several -> the list is surfaced so the first reply asks; none -> you are offered
a new task *or* project-level tracking, which is a valid F&O line and the right answer whenever the
work is not story-shaped. The same hook emits the **unfinalized-days nudge** for every workspace
session (including `Dev`/`own`): days with tracked time whose `/log` never ran. Forgetting to wrap
up costs nothing in hours — idle gaps are discarded (§3) and `rollup.py` finalizes missed days in
bulk (§5) — so the nudge exists for the parts that *do* decay: `CONTEXT.md` handoff and memory
distillation, which need the conversation that a forgotten session takes with it. **The task granularity is the user story / Azure DevOps work item** — the
thing `fno_task:` points at. Sub-steps of one story ("create the datastore", "type-2 history",
"build the model") are deliberately not modelled: F&O has no dimension below Task. A task need not
be finishable in one sitting — the tag is stamped **per turn**, so `/switch-task` mid-session splits
the time exactly where you switched.

**Three levels, rolled up from any depth** (decided 2026-07-28): a session anywhere inside a project --
including sub-folders like `src/...` -- bills to the **project**; a session at a customer node
(`customers/<client>`, above its projects) bills to the **customer** as `customers/<client>` (Proj ID
`UNSET` -- the node has no `fno_code` -- reassigned or left at the review gate); anything else under
`C:\Dev` bills to **Dev**. Sessions outside `C:\Dev` are not tracked at all. A depth-3 folder counts as
a project only if it has a `CLAUDE.md` -- a grandfathered flat code repo under a customer (e.g.
`Tystofte/PowerPortal.wiki`) bills to the customer, and a non-project folder under `own/` bills to `Dev`.
Attribution keys are canonicalized via `realpath` (casing, junctions), so one project never splits into
case-variant rows.

**Registration (fixed 2026-07-28):** hooks registered only in `C:\Dev\.claude\settings.json` never fired
for sessions rooted *below* `C:\Dev` -- Claude settings do not cascade (see memory record
`hooks-subdir-session-gap`; DataCompare and Element Logic sessions went untracked). The
`track_time.py` + `capture_turn.py` hooks are therefore registered in the **user-level
`~/.claude/settings.json` as well**, with identical command strings, so every session on the machine
fires them; the scripts themselves ignore any cwd outside `C:\Dev`. Claude Code **deduplicates identical
hook command strings** across settings files (hooks docs), so the dual registration runs once per event --
**keep the two command strings byte-identical; that identity is load-bearing** (if they diverge, both run
in parallel: harmless for hours -- the rollup merges overlapping intervals -- but `capture_turn.py`'s
daily-file rewrite is not parallel-safe). A turn can legitimately Stop several times (yield on background
work, then continue); every Stop writes a heartbeat and later ones extend the interval.

Known limits (accepted 2026-07-28): a session whose hook payload carries no `cwd`, or one opened through
an alias of `C:\Dev` that `realpath` cannot resolve to it (e.g. a UNC path), is not tracked; subagent
turns are covered via the parent turn's `Stop`; the hooks fail silent by design (exit 0 always), so there
is no runtime alarm if `python` itself is unavailable.

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
The active task lives in `ops/time/active-task` (set by the session-start hook, `/task start` or
`/switch-task`; cleared by `/task done|cancel` or `/switch-task off`). Its two guards -- same-customer
and session-scoped -- are described above. `own/…` and workspace (`Dev`) sessions have no task level;
they bill to the project id (or `INTERNAL-RND`).

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

### Backup (decided 2026-07-06)

The data dirs are gitignored (above), so the workspace's git remote does not protect them. The
backup is a plain mirror to OneDrive, run **as the last step of `/log`** (the same gate that
finalizes days):

```
robocopy "C:\Dev\ops\time" "%OneDrive%\Backup\Dev-ops-time" /E /R:2 /W:5 /NP
```

Robocopy exit codes 0-7 are success. `/E` copies without deleting on the target (a deleted local
file survives in the mirror -- fine for a backup). **By hand / other LLM:** run the same command,
or simply copy the `ops/time/` folder to the OneDrive path.

## 6. Timesheet (the export)

`timesheet/<YYYY-MM>/<date>.md` -- a table with columns **Project | Proj ID | Activity | Task | Hours |
Billable**, one row per F&O line (project id + activity + task), hours rounded to 0.25 h (min 0.5 h),
with billable vs internal totals. Copy the rows straight into F&O time entry (Project ID -> Activity ->
Task -> hours).

**The daily file is the unit of F&O entry** -- time is entered per date. The `--week`/`--month` report
modes (section 5) are just the daily files stacked into one by-date view for a week or a month, so you
can pull a whole period at once without a separate aggregate file.
