Show and roll up tracked working time per project (and tagged task). Time is captured automatically as heartbeats by the `track_time.py` hook; this command reads `ops/time/` and runs the rollup. The full model lives in `ops/time/README.md` and `AGENTS.md` > Time tracking.

Usage:
  /time              ← show today's live tally (writes nothing)
  /time rollup       ← finalize any missed complete days (+ runs the coverage check)
  /time check [YYYY-Www]  ← weekly coverage check vs the full-day rule (default: this + last week)
  /time week [YYYY-Www] [raw]  ← by-date report for one ISO week (default: current week; writes nothing)
  /time month [YYYY-MM] [raw]  ← by-date report for one month (default: current month; writes nothing)

The week/month reports are **consolidated** by default (`--merge`): each project's sub-2 h daily
entries are grouped per week onto one day (<= 9 h/day) so there are not many tiny entries. Add `raw`
to see every entry unmerged.

## Instructions

### `/time` — live tally

Run `python C:\Dev\ops\time\rollup.py --preview` and show the output verbatim (it prints today's
running per-project/task tally). Add one line if anything reads `UNSET`
in the F&O code column: that project's `CLAUDE.md` `## Identity` block is missing `fno_code:`.

### `/time rollup` — finalize + catch-up

Run `python C:\Dev\ops\time\rollup.py`. It finalizes every complete past day that has heartbeats but
no timesheet yet (catch-up for missed days), as **measured** time — nothing is topped up
automatically (README section 8). It then prints the coverage check. Report which days it wrote and
act on the check as below. This is also run as part of `/log`.

### `/time check [YYYY-Www]` — weekly coverage check

Run `python C:\Dev\ops\time\rollup.py --check [YYYY-Www]` and show the output verbatim. Writes
nothing. Then **act on the two action sections**:

- **Unaccounted workdays** — a past workday with no keyboard time and no absence entry. **Ask the
  user, one closed question, listing the dates:** vacation / holiday / sick / offline (which
  project?). Write the answers into `C:\Dev\ops\time\absence.md` (append rows, keep it date-sorted),
  then re-run the check. An `offline` row is claimed as a full day at the next rollup.
- **Days under a full day** — listed with the weighted hours the value model supports. These are
  **never** changed automatically, and a single short day is not by itself a problem: the unit that
  matters is the week or the month.

The month-to-date line is the goal: 7.5 h x elapsed workdays, less recorded absence. If a period
reads short and there are no unaccounted days, close it deliberately — see below.

### `/time topup <YYYY-Www|YYYY-MM>` — close a period to 100%

Run `python C:\Dev\ops\time\rollup.py --topup <period>` and show the output. It is a **dry run**:
it prints the shortfall, the proposed lift per day, and the weighted hours behind each one. Days
whose value record does not cover the claim are flagged.

Only add `--apply` when the user says so, quoting the flagged days first if there are any. Every
file it writes records `measured -> claimed` and the period being closed. No day is ever lifted
above 7.5 h and weekends are never lifted.

### `/time week [YYYY-Www]` / `/time month [YYYY-MM]` — by-date report

Run `python C:\Dev\ops\time\rollup.py --week <arg> --merge` (or `--month <arg> --merge`) and show the
output verbatim. Omit the period arg for the current week/month. **Include `--merge` by default** (the
consolidated view); only drop it if the user's args include `raw` (or `full`/`unmerged`). The report is
**by date** (one row per date/project/task) for F&O entry, read from the finalized
`timesheet/<YYYY-MM>/<date>.md` files with a live-heartbeat fallback for any unfinalized date (marked
`live`). With `--merge`, each project's sub-2 h daily entries are summed per ISO week onto one day,
never pushing a day over 9 h; days already over 9 h from untouched >=2 h entries are flagged, not
changed. Writes nothing.

Keep it mechanical: this command only reads/derives — it never edits heartbeats. Corrections are made
by editing the relevant `ops/time/timesheet/<YYYY-MM>/<date>.md` file directly.
