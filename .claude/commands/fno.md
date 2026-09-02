Register a period's tracked time into Dynamics 365 F&O — the week and month close. Runs the fixed sequence: pre-flight, pull the rows at the F&O entry figure, validate every dimension, enter one journal per ISO week per company, reconcile, approve. The domain knowledge each step needs lives in the `fno-time-registration` skill (it fires automatically here); the time model itself is `ops/time/README.md`.

Usage:
  /fno                 ← close the last complete ISO week
  /fno 2026-W36        ← close one ISO week
  /fno 2026-08         ← close a month (the usual month-close)
  /fno preflight 2026-08   ← run only the gates, enter nothing
  /fno rows 2026-08    ← only produce the paste-ready rows, enter nothing

$ARGUMENTS

## Instructions

This command touches a **production ERP**. It never posts, it never guesses a dimension, and it
stops rather than improvising. Work one step at a time and report at each gate.

### 1. Resolve the period

Parse `$ARGUMENTS` for `YYYY-Www` or `YYYY-MM`. No period given → the last **complete** ISO week.
State the period and the ISO weeks it spans before doing anything else. A month close is a set of
week journals, one per ISO week the month touches, per company.

### 2. Pre-flight — four gates, all before the first line

Run them in order and report each result. **Any red gate stops the run** and becomes a closed
question to Niels.

1. **Already registered?** Check F&O for lines in the period that sit **outside** the journals you
   are about to create — posted or unposted. An unexplained existing line in the period is a **stop**.
   Mechanically: Timekladde → `Vis` = **Bogført**, list every journal in the period beyond the ones
   you are about to create, open `Linjer` and compare dates and project ids against
   `ops/time/timesheet/<YYYY-MM>/`.
   **Read journals, never the utilisation page.** That page counts only posted lines *and lags*. In
   the 2026-08 close it read 33,00 h mid-posting and was taken as evidence of a second source,
   raising a false double-registration alarm; the next day it read the full 145,00 h — it had been
   showing our own time all along. A stale total is not a second total
   (`ops/tasks/done/2026-09-01-fno-august-double-registration-check.md`).
2. **Days finalized.** `python C:\Dev\ops\time\rollup.py` — finalizes any complete day still missing
   a timesheet. A period with unfinalized days is not ready to enter.
3. **Coverage.** `python C:\Dev\ops\time\rollup.py --check <YYYY-Www>` for each week in the period.
   Act on **Unaccounted workdays** by asking Niels (vacation / holiday / sick / offline) and writing
   `C:\Dev\ops\time\absence.md`, then re-run. **A short period is a question about the target before
   it is a question about the hours** — never reach for `--topup` here, and never apply one whose
   weighted evidence does not support the lift.
4. **Every dimension resolves.** For every line in the period, the customer's required dimension is
   present (`ops/time/README.md` §4.1) and every task id exists in F&O. **An empty task lookup means
   the task does not exist**, not that it resolved. Collect all unresolved ids and put them to Niels
   in **one** question — do not discover them one at a time mid-entry.

### 3. Pull the rows

Start the dashboard if it is not running: `python C:\Dev\ops\dashboard.py --no-open` (background),
then `http://127.0.0.1:8787/`. Go to the **week timesheet / audit page** (`#timesheet/audit`) and set
the **Month filter** to the period's month.

Three traps, all load-bearing:

- **Copy from the week/audit page, never the Month page.** The same *Copy rows* button yields the
  scaled **F&O entry** figure on the week page and plain **work time** on the month page. F&O entry
  is the source of truth for registration.
- **Clear every customer chip filter first.** *Copy rows* filters on company only and **ignores the
  customer chip filter** — copying with a customer deselected puts more rows on the clipboard than
  are on screen. Always copy with all customers shown, then reconcile the row count against the
  block.
- **One block per company, one copy each.** The payload has no company column, because the company
  is the block you copied from. PING and PNO1 are separate copies and separate journals.

The clipboard payload is TSV with a header row: `Date, Customer, Project, Proj ID, Activity, Task,
Hours`. Dates are ISO `YYYY-MM-DD`; **hours use a dot decimal** (`7.5`, `1.25`) while F&O expects the
Danish comma — convert on the way in and check the first pasted line before trusting the rest.

Split the copied rows into one set per **ISO week per company** — that is the journal grain.

For `/fno rows`, stop here: hand Niels the per-journal row sets and the totals, and say nothing was
entered.

### 4. Enter — paste, do not drive the grid

**Default: the F&O Excel add-in paste.** Prepare one journal's rows, paste, publish, reconcile that
journal's total against the prepared rows, and only then continue to the next. **Prove the path on
one journal before committing the whole period to it.**

Fill **date, project id, task (or activity), hours** and nothing else — `Kategori` auto-fills once
`Opgave` resolves, and `Timer` is typed because it does not recompute from start/end.

If the Excel path is unavailable, offer Niels the choice between entering from the prepared rows
himself and the browser fallback. Take the browser fallback only on his answer, and then follow
`.claude/skills/fno-time-registration/references/browser-fallback.md` in full — re-screenshot before
every click, verify every write, one journal at a time.

### 5. Approve — Godkendelse → Finished. Never Bogfør.

Per journal: select the journal **row** (F&O acts on the active row, not the checkbox) →
**Godkendelse → Finished** → OK on the *"Kontroller kladde"* dialog → confirm *"Kladden har ændret
status til Finished."*

The journals stay under **"Ikke bogført"**. **Posting is Niels's decision and is never part of this
command.** If asked why utilisation reads low afterwards: it counts only posted lines, and that is
expected.

### 6. Report and record

- Journal ids with hours per company plus the grand total, in the August form:
  `PING 021924 W31 3,50 / 021926 W32 33,00 / … = 138,75 h; PNO1 004431 6,25 h. 145,00 h.`
- State plainly that the journals are **approved, not posted**.
- Name which figure each customer went out at (F&O entry vs work time) and the precedent behind it.
- Anything newly confirmed about a customer's rule goes into `ops/time/README.md` §4.1 — that table
  is canonical, not the skill.
- Then `/log` the close.
