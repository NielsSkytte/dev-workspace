# The entry runbook - registering a period in Dynamics 365 F&O

This runbook exists because a seven-hour August close on 2026-09-01 produced eight distinct errors
in a **production ERP**, every one of them caught and corrected by the owner. Each rule below is one
of those errors. Treat them as hard rules, not preferences.

**The numbers are not this file's business.** They come from the dashboard Time page
(`http://127.0.0.1:8787/time`) at the **F&O entry** column, and the canonical per-customer
dimension table is `ops/time/README.md` section 4.1. Read those; do not re-derive hours here.

Since 2026-09-21 that page also **checks the rule it is registering against**: each customer's
`fno_requires:` is held against every line, and the *Ready to enter* card names what is short and
how many hours ride on it. A green card answers the fourth pre-flight gate for everything except
whether a task id exists in F&O. A red line is fixable on the page - correct the finalized day, or
set `fno_code` on the project so it stops recurring.

---

## 1. Resolve the period

A month close is a **set of week journals** - one per ISO week the month touches, per company.
State the period and the weeks it spans before doing anything else. No period given: the last
**complete** ISO week.

## 2. Pre-flight - four gates, all before the first line

Run them in order, report each result. **Any red gate stops the run** and becomes a closed question
to the owner.

1. **Is the period already registered?** Look for lines in the period that sit **outside** the
   journals you are about to create, posted or unposted. An unexplained existing line is a **stop**.
   Mechanically: Timekladde -> `Vis` = **Bogfoert**, list every journal in the period, open `Linjer`
   and compare dates and project ids against the finalized days.
   **Read journals, never the utilisation page.** That page counts only posted lines *and lags*. In
   the 2026-08 close it read 33,00 h mid-posting and was taken as evidence of a second source,
   raising a false double-registration alarm; the next day it read the full 145,00 h. It had been
   showing our own time all along. **A stale total is not a second total.**
2. **Days finalized.** `python ops/time/rollup.py`. A period with unfinalized days is not ready.
3. **Coverage.** `python ops/time/rollup.py --check <YYYY-Www>` for each week. Act on
   **Unaccounted workdays** by asking (vacation / holiday / sick / offline), writing
   `ops/time/absence.md`, and re-running. **Never reach for `--topup` here**, and never apply one
   whose weighted evidence does not support the lift - see the vacation case in the skill, section 6.
4. **Every dimension resolves.** Open the Time page, set the month, read the **Ready to enter**
   card. Green means every line carries a company, a Proj ID and whatever that customer registers
   on. A day still accruing cannot be corrected - finalize it first (gate 2).
   **The page cannot tell you whether a task id exists in F&O**, only that one is present. Check the
   ids in F&O, remembering that **an empty task lookup means the task does not exist**. Collect all
   unresolved ids and put them in **one** question.

Then, before entering and while there is still time to act, **check the bonus boundary**:

```
python ops/time/bonus.py <invoiced hours> --basis <Timer per maaned>
```

The bonus is a **step function** on faktureringsprocent, changing only at whole 10% marks.
**89.8% pays the 80% rate**, so the last fraction of an hour before a boundary is worth thousands
of kroner. **Get the basis from F&O, never assume one:** `faktureringsprocent = Fakturerbare timer /
Timer per maaned`, and *Timer per maaned* changes every month - 140,00 / 163,00 / 170,00 / 155,50 /
163,00 for May-Sep 2026. Read it off the utilisation page ("Beregnet nytte per medarbejder per
periode"), which also gives the achieved percentage directly. Assuming a flat 160 put August at
90.6% when it was 93.25% - a whole tier's worth of error. That page also shows *Nytte til stede*
against a **different** denominator (Normtimer); the bonus does not run on it.

Report the tier, the margin, and the distance to the next boundary. A **thin** margin - under 2 h
above the line - is worth saying out loud, because one later correction can drop the whole month a
tier.

**What a near boundary licenses, and what it does not.** It is a reason to go *looking* for hours
that were genuinely worked and never registered: an unlogged meeting, a day where the value model
supports more than the timesheet captured, a customer line sitting in internal. It is **never** a
reason to enter hours that were not worked. If the search comes up empty, the month lands where it
lands; say so and move on.

## 3. Pull the rows

Start the dashboard if it is not running (`python ops/dashboard.py --no-open`), open the Time page,
set the month, pick the week. Two ways off the page, both carrying exactly the rows on screen:
**Copy rows** (TSV, one company) and **Excel** (a workbook, one company or every visible line).

Three traps, all load-bearing:

- **A week and Whole month mean the same thing** (since 2026-09-21): both carry the scaled **F&O
  entry** figure, with Measured and Work beside it per line. Cut journals from the **week** - that
  is the journal grain - and use the month to reconcile. Before that date the month gave plain work
  time and copying from it under-registered; an older note saying "never copy from the month" is
  that, and no longer applies.
- **Reconcile the copied row count against the block total, every time.** *Copy rows* once filtered
  on company alone while the table filtered on company *and* the customer chips, so copying with a
  customer deselected silently put extra rows on the clipboard - an over-registration straight into
  a production ERP. It is one expression now; the reconciliation stays.
- **One block per company, one copy each.** The payload has no company column, because the company
  *is* the block you copied from. PING and PNO1 are separate copies and separate journals.

The clipboard payload is TSV with a header: `Date, Customer, Project, Proj ID, Activity, Task,
Description, Hours`. The workbook adds `Company`, `Line property` (Vestforbraending's `No charge`),
`Not ready`, and the line descriptions as *What it was*. Dates are ISO; **hours come out with a dot
decimal** (`7.5`, `1.25`) while F&O expects the Danish comma - convert, and check the first pasted
line before trusting the rest. The workbook writes them as numbers, so Excel applies the locale.

Split the rows into one set per **ISO week per company**. That is the journal grain.

**Check the lines are described.** `python ops/bin/linedesc.py --check <YYYY-MM>` says which lines
have no written description. It is not a gate - an undescribed line can still be entered - but the
description is what answers "what was this 3.75 h" later, and the transcript it comes from is kept
only about 30 days.

## 4. Enter - paste, do not drive the grid

**Default path: the dashboard's rows into F&O's Excel add-in.** Prepare one journal's rows, paste,
publish, reconcile that journal's total, and only then continue. **Prove the path on one journal
before committing a whole month to it.**

Driving a production F&O grid one coordinate at a time is the thing to stop doing. On 2026-09-01 the
browser extension dropped twice, the tab group was rebuilt three times, screenshots timed out
repeatedly, and the page **rescaled between screenshots** so coordinates went stale mid-sequence.
That put `0,75` into **`Rolle-id`** in a production journal (*"Der kunne ikke findes en entydig
Resource category view-post"*). Twice `Kopier` fired where `Linjer` was aimed, because the toolbar
shifts at narrow widths. A failed `Ny` appended to an existing row and produced `600003600003`.

Order of preference:

1. **Excel add-in paste.**
2. **Manual entry by the owner** from the prepared rows - still faster and safer than a driven grid
   for a handful of lines.
3. **Browser grid driving** - the guarded fallback only, taken on an explicit answer, following
   `browser-fallback.md` in full.

**Never let the browser path become the happy path** in a plan, a report, or a rewrite of this file.

### What is typed, what is not

Fill **date, project id, task (or activity), hours** - plus `Beskrivelse` for Element Logic only.
Nothing else.

| Field | Rule |
|---|---|
| `Timer` (hours) | **Typed directly.** It does **not** recompute from `Starttidspunkt`/`Sluttidspunkt`, and those two are not used at all. |
| `Kategori` | **Leave it.** It auto-fills once `Opgave` resolves. |
| `Aktivitet` | Only where the customer registers on activity. On a task-registering customer, **do not write one**. |
| `Opgave` (task) | The ADO work-item id. An empty lookup means the task does not exist. |
| `Beskrivelse` | **Element Logic only, and required there** - carries the engagement as `<number> <title>`, e.g. `45394 Lineage documentation`. Different work there takes a different text; ask rather than reuse. Blank for every other customer. |
| `Rolle-id` | **Never touched.** If a number lands here, a coordinate went stale - delete the line and re-enter it. |
| `Linjeegenskab` | Carries the charge status. Vestforbraending books `No charge`. |

## 5. Per-customer protocol

**`ops/time/README.md` section 4.1 is canonical.** The snapshot below is dated 2026-09-21 and will
drift - read the table, every run.

| Customer | Proj ID | Registers on | Note |
|---|---|---|---|
| Carl Ras | `230-02` | **Task, always** | Activity is **never** supplied by us - F&O derives it from the task |
| Matas | `212-01` | Task | Activity fills automatically |
| Vestforbraending | `222` | Activity `111749` | **Not billable** - F&O books it `No charge` |
| Element Logic | `6001-01` | Activity `600003` | **Company PNO1**, `Opgave` blank, `Beskrivelse` required |
| Tystofte | `4048-1` | Activity `datakilder` | |
| Aeven | `4058` (company PDK4) | Activity | `400760` |
| Finansforbundet | `4053-01` | Activity `Moeder` | |

The three that were **errors**, and so do not change with the table:

- **Carl Ras - Task always, Activity NEVER.** Said three times in one session before it stuck.
  Everything worked on at Carl Ras needs a task.
- **Element Logic lives in company PNO1** (Pingala Norge AS), not PING. Found only by noticing that
  no `6001-01` existed in any PING journal, then reading the posted July PNO1 journal.
- **Element Logic is the one customer where `Beskrivelse` carries the engagement, and it is
  required.** `<number> <title>`; for the lineage work, `45394 Lineage documentation`. That is where
  the `45394` belongs - it is **not** the Task field. Other work there takes a different text.

**Billable is not the same as a customer folder.** The rollup marks every customer project billable;
Vestforbraending is the known exception, and any billable total spanning its hours overstates by
that much.

## 6. Journals - one per ISO week, per company

Named `NSC-<Month>-W<nn>` in PING. Element Logic gets its own journal in PNO1.

**A line that arrives after its journal is posted cannot be added to it.** On 2026-09-01 an Element
Logic 07-08 line of 0,50 h was **dropped** on the owner's instruction rather than opening a new PNO1
journal for a single line. That is the precedent: for one small line, ask; do not open a journal on
your own initiative. Leave an empty journal alone.

## 7. Close - Godkendelse -> Finished. Never Bogfoer.

The month-close step is **approval**, not posting. On 2026-09-01 the close was begun with `Bogfoer`
and stopped: *"tror bare du skal godkende dem"*.

- Select the journal **row** - F&O acts on the **active row**, not the checkbox.
- **Godkendelse -> Finished**. A *"Kontroller kladde <journal>"* dialog appears with batch settings;
  OK returns *"Kladden har aendret status til Finished."* An unconfirmed approval is an unapproved
  journal.
- The journals **stay under "Ikke bogfoert"**. Finished is an approval state.
- **Posting is a separate, later decision and it is the owner's. Never initiate it.**

**Consequence for reporting:** the utilisation page counts only **posted** lines. A low figure right
after a close is expected and is **not** evidence of missing registration - August read 33,00 h
while 138,75 h sat approved-but-unposted. Do not "fix" it.

## 8. Reconcile and record

- Reconcile **per journal as you go**, not once at the end: the journal's total against the rows
  prepared for that week and company.
- Report as journal ids with hours per company plus the grand total:
  `PING 021924 W31 3,50 / 021926 W32 33,00 / ... = 138,75 h; PNO1 004431 6,25 h. 145,00 h.`
- State explicitly that the journals are **approved, not posted**.
- Name which figure each customer went out at, and the precedent behind it.
- Anything a customer's rule turned out to be goes into `ops/time/README.md` section 4.1 - that
  table is the canonical home, not this file.
