---
name: time-tracking-to-fno
bundle: custom
description: >
  The workspace's time-tracking chain, from a keystroke to an approved Dynamics 365 F&O journal
  line, and the knowledge each step of the `/fno` week and month close needs. Use it for any
  request about how time is captured, attributed to a project or task, rolled up into a finalized
  day, corrected, topped up, reviewed or reported - heartbeats, the 15+5 model, the five measures
  from keyboard to value time, the registers, absence, the day cap. Use it equally for entering,
  correcting, approving or reconciling time in F&O: project ids, activities, tasks, companies,
  journals (kladder), Godkendelse versus Bogfoer, F&O error messages, the utilisation page and the
  faktureringsprocent bonus boundary, in Danish or English. Use it even when the request names one
  link only, such as one day's hours or one customer's project id. The canonical per-customer table
  is `ops/time/README.md` section 4.1; the hours to enter come from the dashboard Time page.
---

# Time tracking, end to end

One chain, six links. Time is **measured** automatically, **reviewed** by a human, **scaled** into
an entry figure, and **typed** into a production ERP.

```
keystroke -> heartbeat -> attribution -> rollup (finalized day) -> F&O entry figure -> journal line -> approved
   S1           S1            S2              S3                        S4              S7            S7
```

Two rules hold the whole thing together:

1. **Raw capture is immutable; the reviewed output is the truth.** Heartbeats are append-only. You
   correct hours by editing the finalized day file, **never** the heartbeats. Every derived number
   heals on a re-read; nothing you fix by hand is ever recomputed away.
2. **Nothing is invented.** A dimension that does not resolve, an hour the evidence does not
   support, a task id that reads blank - each one is a question for the owner, not a gap to fill.
   Entry touches a production ERP.

## 0. What the system is on disk

```
ops/time/
  README.md          the spec + the by-hand recipe (source of truth for the model)
  rollup.py          measured time, finalize, reports, topup   (accelerator; sections 3, 6)
  value.py           keyboard time, tiers, value, stalls       (accelerator; section 4)
  heartbeats/        raw, append-only: one JSONL per UTC date         regenerable: no
  timesheet/YYYY-MM/YYYY-MM-DD.md  the finalized day - the unit of entry   regenerable: yes
  lines/YYYY-MM/YYYY-MM-DD.md      one sentence per line: what it was      regenerable: yes
  value/YYYY-MM-DD.md|.jsonl       the audit record behind a charge        regenerable: no*
  absence.md  not-invoiced.md  session-lines.md  fno-tasks.md  stalls.md   regenerable: no
  active-task        the session's current task marker
```

\* `value/` is derived from the LLM transcripts, and those age out after ~30 days. Once a day's
transcript is gone the record cannot be rebuilt - so `value/`, and every hand-written register
beside it, must be backed up (section 6).

`heartbeats/`, `timesheet/` and `active-task` are gitignored: operational output, regenerable, and
a git history of hour-by-hour changes is noise. `absence.md`, `not-invoiced.md`,
`session-lines.md`, `fno-tasks.md` and `stalls.md` are tracked - they are decisions, not
derivations.

The model is tool-neutral. Any LLM, or a human with a text editor, can run it; see
`references/setup-and-by-hand.md`.

## 1. Capture - one heartbeat per turn

Every turn appends one JSON line to `heartbeats/<utc-date>.jsonl`:

```json
{"ts_start":"2026-06-22T06:14:03Z","ts_end":"2026-06-22T06:51:20Z","project":"customers/Melbye/data-agent-offer","session":"abc12345","task":"2026-06-15-melbye-data-agent-offer"}
```

`ts_start` = when the prompt was sent, `ts_end` = when the turn finished, both UTC. Several
heartbeats per turn are harmless - they collapse into one stretch in section 3.

**Three capture defects are handled, and each one had put phantom hours on a customer line.** Know
them, because they are why the numbers are shaped the way they are:

| Defect | What happened | The guard |
|---|---|---|
| A turn that asks a question stays open | A question issued 09:15 and answered 14:25 wrote a 325 min heartbeat, 310 of it the question sitting there (2026-08-20) | The capture hook also fires on the question tool, so the turn is written as its **active segments**, one heartbeat each. A question answered in seconds is ordinary turn time and is not cut. |
| A turn can end without having started | A `!`-prefixed shell input re-ended a session at 16:03 reusing a `ts_start` from 10:24 - 5.5 phantom hours (2026-08-03) | A later end only extends a turn if it lands **within the 15 min idle timeout**; beyond that the heartbeat becomes a point and the idle time is discarded. |
| The end hook does not always fire | 8 of 1,422 heartbeats spanned over 60 min; **every one held at most 20 minutes of activity around a 5-13 hour hole** | One heartbeat is **bounded at 60 min** on the derive side. The bound cannot tell a stalled turn from a long one, so it never truncates silently - see *Bounded turns*, section 3. |

Other blocking waits - a permission prompt, a classifier timeout - are invisible to capture. The
60 min bound and the stall review are the guard for those.

## 2. Attribution - the task decides, the folder is the fallback

**The active task decides the project; the session's working directory is the fallback.** A project
routinely spans several repos and a repo hosts several tasks, so a folder cannot express which work
is in play. Per turn:

1. An active task that passes both guards -> its project is the project, and the heartbeat carries
   the task tag.
2. Otherwise -> the working directory, no task tag.

**Two guards, both load-bearing:**

- **Same customer only.** A task overrides the folder only within the same customer. A customer
  node is overridden by a task on one of its projects, which is how node-level `UNSET` resolves
  itself. **Internal (`Dev`, `own/...`) is never overridden** - moving internal time onto a
  customer is the direction that over-bills, so it stays a deliberate call at the review gate.
- **Per session.** The marker holds one entry **per session**. A session reads only its own, so a
  tag left set on Monday, or running in another window on another customer, never applies here.
  Write it with the merge-safe helper, **never by overwriting the file**, or you wipe the other
  open sessions' entries.

**Three levels, rolled up from any depth:** a session anywhere inside a project - including
subfolders - bills to the **project**; a session at a **customer node** (above its projects) bills
to the **customer**, which has no project id and so can never produce an enterable line; anything
else in the workspace bills to **Dev**. Sessions outside the workspace are not tracked at all. A
folder counts as a project only if it carries its own `CLAUDE.md`. Keys are canonicalized through
`realpath`, so casing and junctions cannot split one project into two rows.

Within a project, which files you touch is irrelevant - attribution follows the session, not the
edits. A cross-edit between two real projects is noise that washes out.

**One override, at the review gate: `Dev` -> a project. Never project -> project.** `Dev` is the
catch-all, not a billing target; when its time is clearly one project's work, move it. Time on a
named project stays there, and time is never reassigned between two named projects by judgement.

**The task granularity is the user story / work item** - the thing the F&O Task dimension points
at. Sub-steps of one story are deliberately not modelled: F&O has no dimension below Task. The tag
is stamped **per turn**, so a task need not be finishable in one sitting, and switching mid-session
splits the time exactly where you switched.

**Setting the task is not a ritual you must remember.** Session start resolves it: exactly one open
task on the project -> set automatically; several -> the list is surfaced and the first reply asks;
none -> a new task *or* project-level tracking, which is a valid F&O line and the right answer
whenever the work is not story-shaped.

**Drift is reported, not corrected.** When a turn cannot carry what its customer registers on, that
is said at the time - once per session per kind - and shown on the dashboard's Today page:

| | |
|---|---|
| `no-task` | no task held, the held task has no work-item id yet, no activity, or no project id |
| `elsewhere` | a task IS held, but on another customer, so the tag was dropped |
| `node` | the turn landed on a customer node itself |

Internal time is silent: it is never entered, so it cannot be short of anything. **Relay the drift
notice and offer to switch task; never just carry on.** On 2026-09-21 twelve turns of customer work
across two sessions were billed with no task, and a single `cd` into a customer node to run one git
command produced a line with no project id. None of it said anything at the time - which is why it
says something now.

## 3. Rollup - the 15+5 active-time model

A session can sit open for days. **Idle gaps are never counted.** Per **(local date, project,
task)** group:

1. Take the group's heartbeats as intervals, sorted by start.
2. Merge into **stretches**: a gap **<= 15 min** extends the current stretch; a gap **> 15 min**
   closes it and starts a new one. The idle gap is discarded - this is what makes a session left
   open for a week cost nothing.
3. Each stretch = its span **+ 5 min** tail buffer (reading and thinking after the last reply).
4. Group hours = sum of stretches, **rounded to 0.25 h**, then **floored to 0.5 h**: any logged
   work on a line that day counts as at least half an hour.

Constants: idle timeout **15 min**, tail buffer **5 min**, one-heartbeat bound **60 min**, rounding
**0.25 h**, floor **0.5 h**. Bucketing is by **local** date; heartbeats are stored in UTC, and an
interval crossing local midnight is **split** and attributed to both dates. Before that split,
2026-08-27 finalized at 22.75 h while 2026-08-28 read as empty.
A session the owner gave only **one prompt** is dropped on read - work never started is not time;
from the second prompt it counts (`lib/heartbeats.without_single_prompt`, README section 3).

Known edges, both small: bouncing between two projects inside 15 min lets one stretch span the
other's detour, and a stretch crossing midnight pays two tail buffers. The daily review gate is
where anything that looks wrong gets fixed.

**Bounded turns.** When the rollup bounds a turn at 60 min it **names it in that day's file** -
which session, when it started, how long it ran, how much was withheld - and the decision belongs
to the review gate. To see *why* it ran that long, run the stall check; it prints the busy minutes,
the largest gap, the messages either side of it and any error at the gap, then appends the finding
to `stalls.md`. If the turn really was working, correct the **day file** by hand and note it in the
verdict column.

Run the stall check at **every** review gate, not only when a flag appears: it is cheap, it is
idempotent, and the window is short - transcripts survive roughly **30 days**, so a finding not
captured inside that window is gone. That is exactly why five bounded turns from June and July read
`no transcript`. A weekly cadence is safely inside it; month-end-only is not.

## 4. From keyboard time to the F&O entry figure

This is the link people get wrong. There are **five** measures, not one, and only one of them is
what gets registered:

| # | Measure | What it is | Role |
|---|---|---|---|
| 1 | **keyboard** | raw measured keyboard time | evidence |
| 2 | **measured** | the 15+5 model, section 3 | control |
| 3 | **work time** | what the 15+5 model claims | the **floor** |
| 4 | **F&O entry** | what actually gets registered | **the source of truth for entry** |
| 5 | **value time** | the weighted figure, from what the session produced | the **ceiling**, never exceeded |

Divergence between 1 and 2 means the model has drifted from what was observed. It is a check, not
a bill.

**Why an intermediate figure exists at all.** One week measured 32.75 h of work against 82.5 h of
value. Billing either end is wrong: work time throws away delivered value, value time bills a
ceiling. The owner's words: *"i want to bill the customer something in between."*

```
entry = work + (1 - e^-x) * (value - work)        x = turns/(10*work) + files/(8*work)
```

rounded to 0.25 h, floored at `work`, capped at `value`. 10 and 8 are the p90 turn- and
file-densities per work hour. The reasoning: **density of work, not duration, moves a line from
measured time toward its value.** Ordinary density lands the entry near work time; dense work
approaches the ceiling. The total is spread across a block's rows so the block sums to it exactly.

**The entry figure is computed in the entry page and nowhere else.** A command-line week or month
report gives **work time**, not entry hours. Do not quote one for the other.

**Which figure a customer goes out at is a precedent, not a fresh derivation.** August 2026: one
customer at the **F&O entry** figure (132.25 h against 90.00 h work time), another at **work
time**, matching how the previous month had been registered there. Carry the precedent forward and
state it in the report. **No precedent -> ask.**

The value model behind measure 5 - keyboard-time measurement, the five tiers and their multipliers,
deliverable-class weights, repeat-work detection, the caps, and what the audit record contains -
is `references/value-and-entry-figure.md`. Read it before defending or changing a charge.

## 5. The registers - decisions that override derivation

Five files carry judgements the derivation cannot make. Each is **append-only**, a later row wins,
and each is honoured by everything downstream.

| File | Says | Consequence |
|---|---|---|
| `absence.md` | a workday had no keyboard time, and why | `vacation`/`holiday`/`sick` drop the day from the target and get no timesheet; `offline` (worked, away from this keyboard) **keeps** the day and is claimed as a full day on a named project |
| `not-invoiced.md` | this line is **never billable**, whatever the folder says | registering time, fixing the setup, building the tooling - done under a customer folder, not on that customer's invoice. Honoured when a day is derived **and** while a day is still running |
| `session-lines.md` | which session inside a grouped line belongs to which task | one day's three sittings on one customer group into **one** line, which is right for billing and wrong for entry. A split **moves** hours between lines of the same day, in 0.25 h steps, never creating or dropping any |
| `fno-tasks.md` | what a task id is actually called | **display only.** The Task column takes the id and nothing else - a name there is rejected by F&O and would be wrong on an invoice. It also flags an id F&O would reject: letters, digits and dashes only |
| `stalls.md` | why a bounded turn ran long, and the verdict | section 3 |

`not-invoiced.md` is **not** the same as a `No charge` line. A `No charge` line **is** entered,
carrying that property; a not-invoiced line is not entered at all. Either way the hours stay
attributed to the client, so the cost of serving them stays visible.

**Direction is the safety rule.** Off a customer is always allowed - it reduces what is invoiced.
Internal **onto** a customer over-bills, so it is one line chosen deliberately at the review gate.
One customer to another is refused outright.

**Line descriptions** (`lines/`) are one sentence per line saying what that day's work **was**. A
timesheet row says `230-02 | - | - | 3.00 | yes` and nothing about the work, which costs twice: an
untagged line cannot be placed on a task without reopening the transcript, and an entry figure
above the measured hours has nothing beside it to justify it - the thing a customer or an auditor
asks about. A helper prepares the material and prints the table; **a session writes the sentence.**
A local model wrote these in July and August and was switched off for producing text that
contradicted its own turn. **A line the evidence does not support is left blank. An invented
description on a billing line is worse than none.**

## 6. The review gate and the cadence

A day becomes **final** when its file is written and reviewed. Today is only ever **previewed** -
it is still accruing.

| When | Do |
|---|---|
| **Per session** | the task is set at session start; relay any drift notice |
| **End of day** | finalize complete days (catch-up included), run the **stall check unconditionally**, write missing line descriptions, then **back up** `ops/time/` off the machine |
| **Weekly** | coverage check per ISO week; answer every unaccounted workday into `absence.md` |
| **Week / month close** | section 7 |

Forgetting to wrap up costs no hours - idle gaps are discarded and missed days finalize in bulk.
What decays is the part that needs the conversation: the handoff, and the transcript-dependent
records.

**The day cap (owner, 2026-10-05): 9 h per customer/project per date; 12 h is allowed when the
tracked data supports it. There is no total limit per day.** That grain is the point - "you billed
me 18 hours in one day" is a statement about a *customer*, not about a folder, and a long day split
across two customers is unremarkable because neither can see the other. What the cap prevents is
several days stacking into one. The code does not match the rule yet: `rollup.py` (`DAY_CAP`) and
`value.py` (`CUSTOMER_CAP`) enforce 12 h, and the Time page packs entry rows at 9 h with no 12 h
exception (`packDays`, `ops/web/time.js`). The cap is enforced where hours are **moved**; measured
hours are never moved behind you, so a day over the cap at finalize is **flagged in its own file**
instead - 2026-08-27 finalized at 22.75 h silently and was caught days later. Over the cap,
measured hours **spill** (`rollup.py`) to another date for the same customer within the same ISO
week, largest line first: hours move, never drop, every move is printed, and two identical lines on
one date fold into one so a spill never adds a line to type. If the whole week is already at the
cap the excess stays where it was measured and says so - inventing a date outside the period would
be worse than one honest over-cap day. Value time spills by a different rule (`value.py`: same
month, same week first) - see `references/value-and-entry-figure.md` section 5.

**Consolidation.** A day-entry **>= 2 h** stays where it is. Sub-2 h entries of the same line
within an ISO week are summed onto a single day of that week, preferring a day that line was
actually worked. This is presentation, not measurement.

**The full-period rule.** A normal working week should end up billed in full - but:

| | |
|---|---|
| **Default** | every finalized day carries its **measured** hours. Nothing is topped up automatically. |
| **Target** | 7.5 h x working days in the period, less recorded absence |
| **Scope** | a **week** or a **month**, never a day in isolation. A 3 h Tuesday next to an 11 h Wednesday is a full week. |
| **Ceiling** | no day is lifted above 7.5 h; weekend days are never lifted - weekend hours are claimed as measured, on top of the target. |
| **Evidence** | the weighted figure is printed beside every proposed lift. **A lift past it is a lift with nothing behind it, and is flagged.** |
| **Explicitness** | the top-up is a dry run. Only an explicit apply writes, and every file it touches records `measured -> claimed` and why. |

A top-up goes across days shortest-first - a 3 h day is likelier under-measured than a 7 h one -
then within a day **proportionally across its billable lines**. Internal lines are never inflated:
a top-up is a billing act. It **will not invent a day**. A period short because a workday has no
time and no absence row leaves the hours unplaced and says so; that is a question for `absence.md`,
not a rounding problem.

> **A period reading short is a question about the target before it is a question about the hours.**
> On 2026-09-01 a proposed +17.50 h across three August days was refused because the value model
> supported roughly 1.50 / 0.50 / 1.50 h on them. They were vacation. Marking them moved August
> from 125.00 of 142.50 (88%) to 125.00 of 120.00 (104%) **with not one hour added.**

## 7. F&O entry

### Dimensions

A Dynamics F&O time line is **Project ID -> Activity -> Task**, resolved **additively**: a task adds
its activity and task *beneath* the project id, it does not replace it.

1. **Project ID** - the project's own `fno_code`. Internal -> the internal R&D code. Missing ->
   `UNSET`, and surfaced so it gets set.
2. **Activity** - the tagged task's activity; blank if untagged, or if the customer does not use it.
3. **Task** - the tagged task's work-item id; blank for activity-only customers.

**Grouping is by the finest dimension present.** Rows sharing the full key merge; a task-level line
is never rolled up into its activity, and an activity-level line merges only where there is no
task. Billable = the project is a customer project.

**Which dimension a customer registers on is the customer's rule, not ours**, and it is
machine-readable on the customer node (`fno_requires`, `fno_billable`, `fno_description`, plus
overrides for company, code and activity) so the entry page can say *this line cannot be typed yet*
instead of leaving it to be spotted. **The canonical per-customer table is `ops/time/README.md`
section 4.1 - read it every run; it changes.** The two rules worth repeating here are the ones that
were *errors*, and errors do not change with the table:

- **A task-registering customer gets a Task and NEVER an Activity.** Carl Ras (`230-02`) is the
  case: F&O derives the activity from the task, so writing one is noise at best and contradicts the
  task's own activity at worst. It took three corrections in one session before it stuck, and
  everything worked on there needs a task.
- **A customer can live in a different company.** Element Logic (`6001-01`) registers in **PNO1**
  (Pingala Norge AS), not PING - found only by noticing that its project id existed in no PING
  journal, then reading the posted PNO1 journal. It is also the only customer where `Beskrivelse`
  is **required**, carrying the engagement as `<number> <title>` (`45394 Lineage documentation` for
  the lineage work). Different work there means a different text: **ask, never carry one forward.**

### Rule 0 - never guess a dimension value

A project id, activity, task id or company that does not resolve is a **question for the owner**.
On 2026-09-01 five ids were ambiguous or missing; putting each one back was the single method that
held all day. Guessing any of them mis-bills a customer.

**A task id that does not exist returns an EMPTY lookup, not an error.** Two ids read as blank until
they were created mid-session. Elsewhere, an id returned *"Opgaven eksisterer ikke"* and all its
time booked to the neighbouring id until DevOps created it. **An empty lookup is a missing task,
never a resolved one.** Validate **every** id in the period **before** the first line, and put all
unresolved ids in **one** question - do not discover them one at a time mid-entry.

### The run

The full runbook - the four pre-flight gates, the transport rule, which fields are typed and which
auto-fill, journals one per ISO week per company, the approval step, reconciliation and the bonus
boundary check - is **`references/fno-entry.md`**. Read it before entering anything. Its five hard
rules, in one breath:

1. **Run all four pre-flight gates before the first line.** Any red gate stops the run.
2. **Paste the rows; do not drive the grid.** Driving a production grid one coordinate at a time put
   `0,75` into a role-id field in a production journal. The browser path is the guarded fallback
   (`references/browser-fallback.md`), never the happy path.
3. **Type date, project id, task-or-activity, hours. Nothing else.** Hours are always typed: they
   do not recompute, and they pre-fill from the task; the category auto-fills once the task resolves.
4. **One journal per ISO week per company. Reconcile each one before starting the next.**
5. **Closing is Godkendelse -> Finished. Never Bogfoer.** Approval is not posting, and **posting is
   the owner's decision.** Approve last: approved journals can be posted by someone else within
   hours, so every correction comes before approval. A low utilisation figure right afterwards is
   expected - that page counts only posted lines - and is **not** evidence of missing registration.
   Do not "fix" it.

## 8. Reporting a run

- Journal ids with hours per company, plus the grand total:
  `PING 021924 W31 3,50 / 021926 W32 33,00 / ... = 138,75 h; PNO1 004431 6,25 h. 145,00 h.`
- State plainly that the journals are **approved, not posted**.
- Name **which figure each customer went out at** - entry or work time - and the precedent behind it.
- Anything newly confirmed about a customer's rule goes into the canonical per-customer table, not
  into this skill.

## Companion files

| File | For |
|---|---|
| `references/value-and-entry-figure.md` | the value model: keyboard time, tiers, weights, repeat work, caps, the audit record |
| `references/fno-entry.md` | the entry runbook: pre-flight, transport, fields, journals, approval, bonus boundary |
| `references/browser-fallback.md` | driving the F&O grid when paste is unavailable - guarded, never default |
| `references/setup-and-by-hand.md` | what to install, what to change on another machine, and how to run the whole model by hand |
