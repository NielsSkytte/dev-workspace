---
name: fno-time-registration
bundle: custom
description: >
  Registering tracked time into Dynamics 365 Finance and Operations - the weekly and monthly close.
  Covers which F&O dimension each customer accepts (Carl Ras task-only, Element Logic activity-only
  in company PNO1, Matas ADO task, Vestforbraending No charge), which fields on a journal line are
  typed and which auto-fill, why a close is Godkendelse -> Finished and never Bogfoer, how journals
  are cut one per ISO week per company, the pre-flight checks that run before a single line is
  entered, and the transport rule that the Excel add-in paste is the default and driving the F&O
  grid through a browser is the guarded fallback. Use this skill whenever time is being entered,
  corrected, approved or reconciled in F&O, whenever a timesheet is being prepared for entry, and
  whenever a question is about an F&O project id, activity, task, journal or company. Trigger on
  "register time", "month close", "week close", "close August", "enter the timesheet", "F&O time",
  "tidsregistrering", "timeregistrering", "godkend kladden", "Bogfoer", "Godkendelse", "Finished",
  "journal / kladde", "which project id for X", "which activity for X", "the hours are not showing
  in utilisation", "Opgaven eksisterer ikke", "Rolle-id", "Linjeegenskab", "No charge", or any
  Dynamics 365 F&O timesheet or project-journal work. The per-period run sequence is the `/fno`
  command; this skill carries the knowledge each of its steps needs. Companion knowledge: the
  canonical per-customer table is `ops/time/README.md` section 4.1, and the numbers to enter come
  from the dashboard week/audit page. Use this skill even if the request names only one piece
  (e.g. just "what project id is Carl Ras" or "should I post these journals").
---

# Registering time in Dynamics 365 F&O

This skill exists because a seven-hour August close on 2026-09-01 produced eight distinct errors in
a **production ERP**, every one of them corrected by Niels. Each rule below is one of those errors.
Treat them as hard rules, not preferences.

The numbers themselves are not this skill's business. They come from the dashboard week/audit page
at the **F&O entry** column (`ops/memory/store/dashboard-fno-entry-measure`), and the canonical
per-customer dimension table is **`ops/time/README.md` section 4.1**. Read those; do not re-derive
hours here.

---

## Rule 0 - never guess a dimension value

A project id, activity, task id or company that does not resolve is a **question for Niels**, not a
gap to fill with the nearest plausible value. On 2026-09-01 five ids were ambiguous or missing
(490 -> 496 -> 490, 493 -> 553, and both 555 and 524); putting each one back to Niels was the single
method that held all day. Guessing any of them mis-bills a customer.

**A task id that does not exist returns an EMPTY lookup, not an error.** `CarlRData-555` and
`CarlRData-524` both read as blank until Niels created them mid-session. An empty lookup is a
missing task, never a resolved one. Same in Matas: `Task-65904` returned *"Opgaven eksisterer ikke -
nye opgaver boer oprettes via DevOps"* and all its time books to `Task-65905` until DevOps creates
it.

Validate **every** id in the period **before** entering the first line, not as you hit it.

---

## 1. Transport - paste, do not drive the grid

**Default path: the dashboard's Copy rows into F&O's Excel add-in.** Driving a production F&O grid
one coordinate at a time is the thing to stop doing. On 2026-09-01 the browser extension dropped
twice, the tab group was rebuilt three times, screenshots timed out repeatedly, and the page
**rescaled between screenshots** so coordinates went stale mid-sequence. That put `0,75` into
**`Rolle-id`** in a production journal (*"Der kunne ikke findes en entydig Resource category
view-post"*). Twice `Kopier` fired where `Linjer` was aimed, because the F&O toolbar shifts at narrow
widths. A failed `Ny` appended to an existing row and produced `600003600003`.

Order of preference:

1. **Excel add-in paste** - prepare the rows, paste one journal, publish, reconcile that journal's
   total, then continue. Prove the path on **one** journal before committing a whole month to it.
2. **Manual entry by Niels** from the prepared rows - still faster and safer than a driven grid for
   a handful of lines.
3. **Browser grid driving** - the guarded fallback only. If you take it, follow
   `references/browser-fallback.md` in full. Its rules are not optional; each one is a defect that
   already reached production.

Never let the browser path become the happy path in a plan, a report, or a rewrite of this skill.

### What Copy rows actually gives you

Three traps, verified in `ops/dashboard.html` on 2026-09-01. Full detail and the code references:
`ops/memory/store/dashboard-copy-rows-transport`.

- **The week/audit page and the Month page share the same button and mean different things.** On the
  week page the hours are the scaled **F&O entry** figure; on the Month page they are plain **work
  time**. Registration uses F&O entry, so **always copy from the week/audit page**.
- **Copy rows ignores the customer chip filter.** It filters on company only. Copying while a
  customer is deselected puts **more rows on the clipboard than are on screen**. Clear the chips
  before copying and reconcile the row count against the block.
- **Hours come out with a dot decimal** (`7.5`, `1.25`, `8`) while F&O expects the Danish comma.
  Convert, and check the first pasted line before trusting the rest.

The payload is TSV with a header: `Date, Customer, Project, Proj ID, Activity, Task, Hours`. There is
**no company column** - the company is the block you copied from, so PING and PNO1 are separate
copies and separate journals. Nothing outside the browser reproduces the entry figure: the scaling
lives only in the dashboard's JavaScript, so `rollup.py --week` and `dashboard.py --json` give work
time, not entry hours.

---

## 2. Pre-flight - before a single line is entered

Run all four. Any of them can stop the close.

1. **Is the period already registered?** Check F&O for lines already posted or entered in the period
   **outside** the journals you are about to create. Open question as of 2026-09-01: the utilisation
   page read 33,00 h for August from lines outside our six journals, which may mean August is
   double-registered. Until that is settled, treat an unexplained existing line in the period as a
   **stop**, and surface it.
2. **Coverage and shortfall.** `python ops/time/rollup.py --check [YYYY-Www]`. A period reading short
   is a question about the **target** before it is a question about the hours.
3. **Absence.** Any unaccounted workday goes into `ops/time/absence.md` first. On 2026-09-01 a
   proposed `--topup` of **+17,50 h** across 24., 25. and 27. August was refused because the value
   model supported roughly 1,50 / 0,50 / 1,50 h on those days. They were vacation. Marking them moved
   August from 125,00 of 142,50 (88%) to 125,00 of 120,00 (104%) with **not one hour added**.
   **Never apply a topup whose weighted evidence does not support the lift**, even under an
   instruction to close the gap. See `ops/memory/store/time-shortfall-can-be-in-the-target`.
4. **Every task id resolves** (Rule 0), and every line has the dimension its customer requires
   (section 4).

---

## 3. Filling a journal line - what is typed, what is not

Fill **date, project id, task (or activity), hours**. Nothing else.

| Field | Rule |
|---|---|
| `Timer` (hours) | **Typed directly.** It does **not** recompute from `Starttidspunkt` / `Sluttidspunkt`, and those two are not used at all. |
| `Kategori` | **Leave it.** It auto-fills once `Opgave` resolves. It is not a field you fill explicitly. |
| `Aktivitet` | Only where the customer registers on activity (section 4). On a task-registering customer, **do not write one**. |
| `Opgave` (task) | The ADO work-item id. An empty lookup means the task does not exist (Rule 0). |
| `Rolle-id` | Never touched. If a number lands here, a coordinate went stale - delete the line and re-enter it. |
| `Linjeegenskab` | Carries the charge status. Vestforbraending books `No charge`. |

Grouping follows the finest dimension present: rows sharing the full (project id, activity, task)
key merge. See `ops/time/README.md` section 4.

---

## 4. Per-customer protocol

**`ops/time/README.md` section 4.1 is canonical for the table** - project ids, the dimension each
customer registers on, and the confirmation date. Read it every run; it changes.

The two rules below are here because they were **errors**, and errors do not change with the table:

- **Carl Ras (`230-02`) - Task always, Activity NEVER.** F&O derives the activity from the task.
  Writing an `activity:` on a Carl Ras line is wrong: noise at best, contradicting the task's own
  activity at worst. Niels said it three times on 2026-09-01 before it stuck. Everything worked on at
  Carl Ras needs a task.
- **Element Logic (`6001-01`) lives in company PNO1**, not PING. PNO1 is Pingala Norge AS. This was
  only found by noticing that no `6001-01` existed in any PING journal and then reading the posted
  July PNO1 journal. Activity `600003` "Operations", `Opgave` blank. The `45394` in the sheet note is
  **not** the Task field.

One more that is documented but not encoded anywhere: **Vestforbraending (`222`) is not billable** -
F&O books it `No charge`, while the workspace still counts every `customers/...` project billable.
Any billable total spanning its hours overstates by that much.

Full detail: `ops/memory/store/fno-registration-per-customer-protocol`.

---

## 5. Journals - one per ISO week, per company

A journal is **per ISO week, per company**, named `NSC-<Month>-W<nn>` in PING. Element Logic gets its
own journal in PNO1.

**A line that arrives after its journal is posted cannot be added to it.** On 2026-09-01 an Element
Logic 07-08 line of 0,50 h was **dropped** on Niels's instruction rather than opening a new PNO1
journal for a single line. That is the precedent: for one small line, ask; do not open a journal on
your own initiative.

Leave an empty journal alone (`PING-021923`, 0,00 h, untouched).

---

## 6. Closing = Godkendelse -> Finished. Never Bogfoer.

The month-close step is **approval**, not posting. On 2026-09-01 the close was begun with `Bogfoer`
and stopped by Niels: *"tror bare du skal godkende dem"*.

- Select the journal **row** - F&O acts on the **active row**, not the checkbox.
- **Godkendelse -> Finished**. A *"Kontroller kladde <journal>"* dialog appears with batch settings;
  OK returns *"Kladden har aendret status til Finished."*
- The journals **stay under "Ikke bogfoert"**. Finished is an approval state.
- **Posting is a separate, later decision and it is Niels's.** Never initiate it.

**Consequence for reporting:** the utilisation page counts only **posted** lines. A low utilisation
figure right after a close is expected and is **not** evidence of missing registration - August read
33,00 h while 138,75 h sat approved-but-unposted. Do not "fix" it.

Detail: `ops/memory/store/fno-month-close-approve-not-post`.

---

## 7. Which figure gets registered

The dashboard week/audit page carries keyboard / measured / work time / **F&O entry** / value time.
**F&O entry is the source of truth for what gets registered**; work time is its floor and value time
its ceiling.

Which figure a given customer goes out at is a **decision with a precedent, not a fresh derivation**.
August 2026: Carl Ras at the **F&O entry** figure (132,25 h against 90,00 h work time); Element Logic
at **work time**, matching how July was registered there. Carry the precedent forward and state it in
the report. If a customer has no precedent, ask.

---

## 8. Reconcile and record

- Reconcile **per journal** as you go, not once at the end: the journal's total against the rows you
  prepared for that week and company.
- Report the close as journal ids with hours, per company, plus the grand total - the August form:
  `PING 021924 W31 3,50 / 021926 W32 33,00 / ... = 138,75 h; PNO1 004431 6,25 h. 145,00 h.`
- State explicitly that the journals are **approved, not posted**.
- Anything a customer's rule turned out to be, that section 4.1 does not already say, goes into
  section 4.1 - that table is the canonical home, not this skill.
