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
  value.py               <- accelerator for the VALUE model (section 7); derive-only
  active-task            <- present only while a task is "started"; holds one task slug (set by /task)
  heartbeats/            <- raw, append-only: one JSONL file per UTC date
    YYYY-MM-DD.jsonl
  timesheet/             <- rolled-up, reviewed output (the deliverable)
    YYYY-MM/             <- one folder per month (keeps the daily pile manageable)
      YYYY-MM-DD.md      <- a finalized day (local date); the unit of F&O entry
  value/                 <- derived value records (section 7); evidence, not the timesheet
    YYYY-MM-DD.md        <- the audit record: keyboard time, tiers, deliverables
    YYYY-MM-DD.jsonl     <- the same, machine-readable
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
week are **summed and placed on a single day of that week**, preferring a day that line was actually
worked.

**The cap: 12 h per customer per date** (decided 2026-08-19). That grain is the point — "you billed
me 18 hours in one day" is a statement about a *customer*, not about a folder, and 12 h across two
different customers is unremarkable because neither can see the other. A single long day for one
customer is normal and stays; what the cap prevents is several days stacking into one.

**Over the cap, hours spill to another date** for the same customer, largest line first, within the
same week. Hours are moved, never dropped: the weekly and monthly totals are identical afterwards,
and every move is printed (`spilled 4.00 h for customers/X from 2026-09-07 to 2026-09-08`). Two
identical F&O lines landing on the same date are folded into one, so a spill never adds a line to
type. If the whole week is already at the cap the excess stays where it was measured and says so —
inventing a date outside the period would be worse than one honest over-cap day.

`/time` runs the reports with `--merge` on by default; pass `raw` to see every entry.

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

## 7. Value model (ADR-004, PROVISIONAL -- re-evaluate end of 2026-08)

Sections 1-6 measure **time**. This section derives a second number, **weighted hours**, from what
the session actually produced, and keeps a **keyboard time** figure beside it so any charge can be
justified. It does not change the timesheet: `rollup.py` still owns section 6, and nothing here is
invoiced automatically. See `ops/decisions/ADR-004-value-based-billing.md` for the reasoning and for
the explicit split between what is derived and what is judgement.

**Evidence source.** Heartbeats give attribution (project, task); the session transcript gives
duration and evidence (which tools ran, which files were written, how many lines). Under Claude Code
the transcripts live in `~/.claude/projects/**/*.jsonl`. This is the one part of the substrate that
depends on a specific tool -- `ops/time/value/` is therefore the durable record and **must be backed
up** (section 5). Another LLM would need to emit an equivalent per-turn evidence stream.

### 7.1 Keyboard time (measured)

A turn runs from the user prompt to its **last production event** (assistant message or tool result),
bounded by *both* the transcript and the heartbeat. The transcript ends a turn whose `Stop` hook never
fired; the heartbeat bounds a turn whose segmentation broke on a resumed session. Both cases are real:
a 1-minute turn on 2026-08-03 recorded a 340-minute heartbeat, and a 131-minute turn on 2026-07-23
contained 8.8 minutes of activity.

Within a turn, each inter-event gap is capped at **5 minutes** -- the same rule already used between
turns (section 3), applied one level down. A pending permission prompt or a long-running tool call is
not keyboard time.

### 7.2 Tiers (derived from tool evidence)

| Tier | Condition | Multiplier |
|---|---|---|
| T1 Junior Assistant | no tools, or <=2 read-type calls | 2.0x |
| T2 Analyst | >=3 reads, or web/docs search, or a subagent spawn | 3.0x |
| T3 Consultant | state-changing execution, or a sub-20-line edit | 3.0x |
| T4 Senior Consultant | >=20 weighted changed lines written | 6.0x |
| T5 Principal Consultant | **per stretch**: >=600 weighted lines, or one new file >=300 | 25.0x |

**The multipliers are judgement, not evidence.** T1-T4 are Niels's estimate of the acceleration; T5
was fitted to one completed deliverable and is exactly determined, therefore untested. Do not cite
the fit as validation. Everything else in this section is derived and reproducible.

Weighted hours = sum over turns of `keyboard minutes x multiplier`, plus gaps (capped at 5 min) and a
5-minute tail per stretch **at 1.0x**, then rounded to 0.25 h with the same 0.5 h floor as section 3.

### 7.3 Deliverable classes

The weight scales the **changed-line count** -- which feeds the tier gates and the repeat-work call --
never the hours directly. Knowledge is denser per line than code.

| Class | Weight |
|---|---|
| `CONTEXT.md`, `README.md`, `CLAUDE.md`, `docs/`, `wiki/` | 2.00x |
| other `.md` | 1.50x |
| code, notebooks, anything else inside a project | 1.00x |
| `ops/memory/` | 0.50x |
| other `ops/` | 0.25x |
| `ops/tasks/`, `ops/time/`, `ops/memory/daily/` | 0.00x |

`ops/memory/daily/` is zero because those records are written by the local summarizer hook, not by
the engagement.

### 7.4 Repeat work

A ledger keyed by file path, rebuilt from scratch on every run (nothing persisted can drift):
a path not seen before is `new`; >=150 weighted lines on a seen path is a `rebuild`; >=30 is a
`revision`; below 30 it is an `adjustment` -- **tier drops one and nothing is credited**.

### 7.5 Caps

| Level | Threshold | Type |
|---|---|---|
| per **customer** per day | 12 h | hard -- spills to another day, same customer, same month |
| all customers per day | 15 h | soft -- review flag only, never moves hours |
| all customers per day | 24 h | hard -- assertion |

A day over 9 h across *different* customers is fine: customers cannot see each other, so the only cap
that binds is the one on their own line. Spill is section 5's `consolidate_week` run backwards, plus
two guardrails: never cross a month boundary (it may be invoiced), and distance beats the worked-day
preference outside the week.

**The 15 h flag counts weighted hours, not clock hours.** It means "check the classifier", never
"you worked 15 hours."

### 7.6 Output

`value/<date>.md` is the **audit record** -- per F&O line: keyboard time, turn and stretch counts, the
tier table with multipliers, and every file touched with its line count, kind and class. This is what
you show when asked to justify a charge. `value/<date>.jsonl` is the same data machine-readable.

Each project block also carries a one-line **`Focus:`** -- the dominant files by share of weighted
lines, with two or more files from one directory collapsed into that directory. It answers "what was
this time actually for" without reading the whole deliverables table, and exists because that question
was only asked after a day had already been billed: 2026-08-04 charged Element Logic for a stretch
that was `describe.py 64%, ops/memory/store/ 28%` -- capability development, not the customer's
deliverable (corrected 2026-08-06).

> **Read `Focus:` as a prompt, not a verdict.** It is computed from file writes only, so a stretch of
> advice, analysis or review that wrote nothing contributes hours but no focus -- and a line reading
> `ops/memory/store/ 100%` means those were the only *files written*, not that the whole line was
> bookkeeping. Use it to decide what to look at, then read the tier table and the transcript.

`value.py` modes:
- `python ops/time/value.py` -- derive every complete past day not yet written. Use at `/log`.
- `python ops/time/value.py --preview` -- today's live tally; writes nothing.
- `python ops/time/value.py --date YYYY-MM-DD` -- one date (rewrites it).
- `python ops/time/value.py --month [YYYY-MM]` -- by-customer report; writes nothing.

**By hand:** for each turn, note the active minutes (excluding any gap over 5 minutes), classify it
against the table in 7.2 using what the turn actually did, multiply, and sum per project per day.

## 8. Full working periods + the deliberate top-up (rule 2026-08-19, ADR-005 v2)

Sections 1-6 measure time; section 7 measures value. This section is about the number that gets
billed, and it rests on one intent:

> **A normal working week should end up billed in full.** Elapsed keyboard time measures how long
> the work took, not what it was worth, and the value model (section 7) usually justifies the full
> day on its own. So the timesheet stays **measured** and closing the last gap is a decision
> somebody makes, not a number the tooling invents.

### 8.1 The rule

| | |
|---|---|
| **Default** | every finalized day carries its **measured** hours. Nothing is topped up automatically. |
| **Target** | 7.5 h x working days in the period, less recorded absence |
| **Scope of a top-up** | a **week** or a **month** -- never a day in isolation. A 3 h Tuesday next to an 11 h Wednesday is a full week; only the period total is meaningful. |
| **Ceiling** | no day is ever lifted above 7.5 h, and weekend days are never lifted -- weekend hours are claimed as measured, on top of the target. |
| **Evidence** | `value/<date>.md` weighted hours are printed beside every proposed lift. A lift past the weighted figure is a lift with nothing behind it, and is flagged. |
| **Explicitness** | `--topup` is a dry run. Only `--apply` writes, and every file it touches records `measured -> claimed` and why. |

```
python ops/time/rollup.py --topup 2026-W33          # what would change
python ops/time/rollup.py --topup 2026-08 --apply   # write it
```

**Where the top-up goes.** Across days first — shortest day first, since a 3 h day is likelier to be
under-measured than a 7 h one — then within a day **proportionally across its billable lines**.
Internal lines (`Dev`, `own/…`, `INTERNAL-RND`) are never inflated: a top-up is a billing act and
internal work is not billed. A day with no billable line spreads it across whatever lines it has.

**What it will not do.** It will not invent a day. If a period is short because a workday has no
time and no absence row, the hours stay unplaced and the report says so — that is a question for
`absence.md`, not a rounding problem. It will not touch a day that is already at 7.5 h, so a
finalized month cannot drift upward on a re-run.

*Superseded: ADR-005 v1 (2026-08-17) floored each worked day to 7.5 h automatically at finalize.
It wrote no day before being replaced — the period, not the day, is the unit that matters, and the
lift is a judgement.*

### 8.2 The absence register

`ops/time/absence.md` -- hand-maintained, one row per workday that had no keyboard time. Kinds:
`vacation`, `holiday`, `sick` remove the day from the week and month target and get no timesheet;
`offline` (worked, not at this keyboard -- meeting, workshop, travel) **keeps** the day in the target
and is claimed as a full 7.5 h on the project named in the row, written at the next rollup.

### 8.3 The check

`python ops/time/rollup.py --check [YYYY-Www]` -- **per ISO week**, and it also runs automatically at
the end of every plain `rollup.py` (so `/log` and `/time rollup` both surface it). Default scope is
the current week plus the previous one. It writes nothing. It reports:

- each day of the week: status (`final` / `live` / `absent` / `empty`), measured hours, and for a day under 7.5 h what the value model supports;
- **week total vs 7.5 h x workdays**, and the shortfall;
- **month to date vs 7.5 h x elapsed workdays**, less absence -- the monthly guarantee;
- **Unaccounted workdays** -- a past workday with no keyboard time and no absence row. These must be
  answered: add a row to `absence.md`. Until then the month target counts them and the month reads short.
- **Days under a full day** -- with the weighted figure beside each, and the `--topup` command to close the period. Nothing is changed.

`absence.md` is tracked in git (unlike the rest of `ops/time/`, which is data); it is a decision
record, not derived output.
