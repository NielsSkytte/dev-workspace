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
4. **Every dimension resolves.** The Time page checks this itself now: open
   `http://127.0.0.1:8787/time`, set the Month, and read the **Ready to enter** card. It holds each
   line against the customer's own rule (`fno_requires:` on the customer node, from
   `ops/time/README.md` §4.1) and lists what is short, with how many hours ride on it. Green means
   every line carries a company, a Proj ID and whatever that customer registers on.
   Fix a red line on the page: click it and either correct the finalized day or set `fno_code` on
   the project so it stops recurring. A day still accruing cannot be corrected — finalize it first
   (gate 2).
   The page cannot tell you whether a **task id exists in F&O** — only that one is present. Check
   the ids in F&O as before; **an empty task lookup means the task does not exist**, not that it
   resolved. Collect all unresolved ids and put them to Niels in **one** question — do not
   discover them one at a time mid-entry.

### 3. Pull the rows

Start the dashboard if it is not running: `python C:\Dev\ops\dashboard.py --no-open` (background),
then `http://127.0.0.1:8787/time`. Set **Month** to the period's month and pick the **Week**.

Two ways off the page, both giving exactly the rows on screen: **Copy rows** (TSV, one company) and
**Excel** (a workbook, one company or every visible line). Use whichever the entry path in step 4
takes.

Three traps, all load-bearing:

- **A week and Whole month now mean the same thing** (changed 2026-09-21). Both carry the
  scaled **F&O entry** figure, with **Measured** and **Work** beside it on every line, so
  either can be copied. Take the week when you are cutting week journals — which is the
  journal grain — and the month when you are reconciling. Before 2026-09-21 the month gave
  plain work time and copying from it under-registered; if you are reading an older note
  that says "never copy from the month", that is why, and it no longer applies.
- **Reconcile the copied row count against the block total, every time.** *Copy rows* used to filter
  on company alone while the table filtered on company *and* the customer chips, so copying with a
  customer deselected silently put extra rows on the clipboard — an over-registration into a
  production ERP. Fixed 2026-09-01 (now `ops/web/time.js`, where the two filters are one expression), but the
  reconciliation stays: what you paste goes into a live financial system.
- **One block per company, one copy each.** The payload has no company column, because the company
  is the block you copied from. PING and PNO1 are separate copies and separate journals.

The clipboard payload is TSV with a header row: `Date, Customer, Project, Proj ID, Activity, Task,
Description, Hours`; the workbook adds `Company`, `Line property` (Vestforbraending's `No charge`)
and `Not ready`. `Description` carries the `Beskrivelse` where a customer requires one -- Element
Logic only. Dates are ISO `YYYY-MM-DD`; **hours use a dot decimal** (`7.5`, `1.25`) while F&O expects the
Danish comma — convert on the way in and check the first pasted line before trusting the rest.

Split the copied rows into one set per **ISO week per company** — that is the journal grain.

**Check the lines are described.** `python C:\Dev\ops\bin\linedesc.py --check <YYYY-MM>` says which F&O lines have no written description (`ops/time/lines/`, README 6.1). It is not a gate — an undescribed line can still be entered — but the description is what answers "what was this 3.75 h" later, and the transcript it comes from is only kept about 30 days. Fill the gaps at `/log` before they age out; the downloaded workbook carries them in *What it was*.

For `/fno rows`, stop here: hand Niels the per-journal row sets and the totals, and say nothing was
entered.

**Then check the bonus boundary — before entering, while there is still time to act.**

```
python C:\Dev\ops\time\bonus.py <invoiced hours> --basis <Timer per maaned>
```

Niels's bonus is a **step function** on faktureringsprocent, changing only at whole 10% marks.
**89.8% pays the 80% rate**, and the last fraction of an hour before a boundary is worth thousands of
kroner.

**Get the basis from F&O, never assume one.** `faktureringsprocent = Fakturerbare timer ÷ Timer per
måned`, and *Timer per måned* changes every month — 140,00 / 163,00 / 170,00 / 155,50 / 163,00 for
May–Sep 2026. Read it off
`https://pingprod.operations.dynamics.com/?cmp=ping&mi=HRMUtalizationEmplTrans_PIN` ("Beregnet nytte
per medarbejder per periode"), which also gives the achieved percentage directly. Assuming a flat 160
put August at 90.6% when it was 93.25% — a whole tier's worth of error. That page also shows *Nytte
til stede* against a **different** denominator (Normtimer); the bonus does not run on it.

Report the tier, the margin, and the distance to the next boundary in the pre-entry summary. A
**THIN** margin (under 2 h above the line) is worth saying out loud, because one later correction can
drop the whole month a tier.

**What a near boundary licenses, and what it does not.** It is a reason to go *looking* for hours
that were genuinely worked and never registered — an unlogged meeting, a day where the value model
supports more than the timesheet captured, a customer line sitting in internal. It is **never** a
reason to enter hours that were not worked, and it never overrides the evidence rule in
`ops/memory/store/time-shortfall-can-be-in-the-target`. If the search comes up empty, the month lands
where it lands; say so and move on.

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

- **Write `ops/time/fno-journals.md`** -- one row per journal line, from what F&O showed (the
  line after saving, the journal total, the approval message), never from the prepared rows.
  Status `Created` until *"Kladden har aendret status til Finished"* is seen, then `Finished`;
  `Posted` once Niels has posted. The Time page reads it: the *In F&O* column (red where it
  differs from the F&O entry) and the *Registered %* tile, the percentage F&O actually holds.
- Journal ids with hours per company plus the grand total, in the August form:
  `PING 021924 W31 3,50 / 021926 W32 33,00 / … = 138,75 h; PNO1 004431 6,25 h. 145,00 h.`
- State plainly that the journals are **approved, not posted**.
- Name which figure each customer went out at (F&O entry vs work time) and the precedent behind it.
- Anything newly confirmed about a customer's rule goes into `ops/time/README.md` §4.1 — that table
  is canonical, not the skill.
- Then `/log` the close.
