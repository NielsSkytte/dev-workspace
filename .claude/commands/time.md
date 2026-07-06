Show and roll up tracked working time per project (and tagged task). Time is captured automatically as heartbeats by the `track_time.py` hook; this command reads `ops/time/` and runs the rollup. The full model lives in `ops/time/README.md` and `AGENTS.md` > Time tracking.

Usage:
  /time              ← show today's live tally (writes nothing)
  /time rollup       ← finalize any missed complete days
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
no timesheet yet (catch-up for missed days). Report which days it wrote (it prints them). This is also
run as part of `/log`.

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
