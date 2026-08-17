#!/usr/bin/env python
"""Roll raw heartbeats up into reviewed timesheets. Tool-neutral accelerator.

The algorithm is the source of truth in ops/time/README.md (section 3, the 15+5 model);
this script just runs it. Pure stdlib, ASCII-only, deterministic.

Modes:
  python rollup.py            finalize every complete past day missing a timesheet (catch-up),
                              applying the full-day floor, then run the weekly coverage check.
  python rollup.py --preview  print today's live tally; write nothing.
  python rollup.py --check [YYYY-Www]  weekly coverage check only (default: this week +
                              last week) + month-to-date vs target; write nothing.
  python rollup.py --week [YYYY-Www]   print a by-date report for one ISO week
                                       (default: current week); write nothing.
  python rollup.py --month [YYYY-MM]   print a by-date report for one month
                                       (default: current month); write nothing.
  ... add --merge to either report   consolidate each project's sub-2 h daily entries
                                       within a week onto one day (<= 9 h/day); still by date.

The --week/--month reports are by DATE (one row per date/project/task) because time is
entered into F&O per date. They read the finalized timesheet/<date>.md files (so manual
corrections are honoured) and fall back to live heartbeats for any date not yet finalized.

Bucketing is by LOCAL date/week; heartbeats are stored UTC. Constants below match the README.
"""
import sys, os, json, glob, re, datetime

ROOT = os.environ.get("TIME_ROOT", r"C:\Dev\ops\time")
DEV_WORKSPACE = os.environ.get("DEV_WORKSPACE", r"C:\Dev")
HEARTBEATS = os.path.join(ROOT, "heartbeats")
TIMESHEET = os.path.join(ROOT, "timesheet")


def daily_dir(date):
    """timesheet/<YYYY-MM> -- daily files are grouped into one folder per month."""
    return os.path.join(TIMESHEET, date[:7])


def daily_path(date):
    return os.path.join(daily_dir(date), date + ".md")

IDLE_TIMEOUT = datetime.timedelta(minutes=15)   # gap that splits an active stretch
TAIL_BUFFER = datetime.timedelta(minutes=5)     # reading/thinking after the last reply
ROUND_HOURS = 0.25                              # F&O increment
MIN_HOURS = 0.5                                  # any work on a project that day -> at least 0.5 h
DEV_CODE = "INTERNAL-RND"                        # Dev bucket = internal R&D, non-billable

# ---------- full-day floor (rule 2026-08-17, README section 8) ----------
# A workday that saw real activity is claimed as a FULL day. Elapsed keyboard time measures how
# long the work took, not what it was worth -- the value model (section 7) is the justification.
FULL_DAY = 7.5              # h claimed for a worked workday
ACTIVE_TRIGGER = 0.5        # h of active time on a workday that makes it a worked day
ABSENCE = os.path.join(ROOT, "absence.md")
ABSENCE_KINDS = ("vacation", "holiday", "sick", "offline")


# ---------- time helpers ----------

def parse_utc(s):
    """'2026-06-22T06:14:03Z' -> aware UTC datetime."""
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=datetime.timezone.utc)


def to_local(dt):
    return dt.astimezone()  # system local tz (no arg = local)


def round_quarter(hours):
    return round(hours / ROUND_HOURS) * ROUND_HOURS


# ---------- load ----------

def load_heartbeats():
    """All heartbeats, each enriched with local-date and iso-week keys (bucketed by ts_start)."""
    out = []
    for path in sorted(glob.glob(os.path.join(HEARTBEATS, "*.jsonl"))):
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        hb = json.loads(line)
                        start = parse_utc(hb["ts_start"])
                        end = parse_utc(hb["ts_end"])
                    except Exception:
                        continue
                    if end < start:
                        end = start
                    ls = to_local(start)
                    iso = ls.isocalendar()
                    out.append({
                        "start": start, "end": end,
                        "project": hb.get("project") or "Dev",
                        "task": hb.get("task"),
                        # passthrough only -- the rollup never groups by it (that would fragment
                        # stretches and add a buffer + 0.5 h floor per session). The dashboard's
                        # internal-hours triage uses it to join a stretch to its memory record.
                        "session": hb.get("session") or "",
                        "date": ls.strftime("%Y-%m-%d"),
                        "week": "%04d-W%02d" % (iso[0], iso[1]),
                    })
        except Exception:
            pass
    return out


# ---------- the 15+5 model (README section 3) ----------

def stretch_hours(intervals):
    """intervals: list of (start,end) aware datetimes. Returns active hours, 15+5 model."""
    if not intervals:
        return 0.0
    ivs = sorted(intervals, key=lambda x: x[0])
    total = datetime.timedelta()
    cur_start, cur_end = ivs[0]
    for s, e in ivs[1:]:
        if s - cur_end <= IDLE_TIMEOUT:
            if e > cur_end:
                cur_end = e
        else:
            total += (cur_end - cur_start) + TAIL_BUFFER
            cur_start, cur_end = s, e
    total += (cur_end - cur_start) + TAIL_BUFFER
    return total.total_seconds() / 3600.0


def group(heartbeats):
    """-> {(project, task|None): [(start,end), ...]} for one day or week's heartbeats."""
    g = {}
    for hb in heartbeats:
        g.setdefault((hb["project"], hb["task"]), []).append((hb["start"], hb["end"]))
    return g


# ---------- F&O dimension resolution (README section 4) ----------
# A time line in F&O is Project ID -> Activity -> Task (Azure DevOps-linked). Project ID always
# applies; Activity and Task are optional sub-dimensions under it (some projects register only at
# activity level, some down to task). Resolution is ADDITIVE -- a tagged task adds its activity/task
# beneath the project's id, it does not replace it.

def _read_field(path, field):
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                low = line.strip().lower()
                if low.startswith(field + ":"):
                    return line.split(":", 1)[1].strip().split("#", 1)[0].strip() or None
    except Exception:
        pass
    return None


def project_id(project):
    """The F&O Project ID for a workspace project folder."""
    if project == "Dev":
        return DEV_CODE
    return _read_field(os.path.join(DEV_WORKSPACE, project.replace("/", os.sep), "CLAUDE.md"),
                       "fno_code") or "UNSET"


def task_dims(slug):
    """(activity, fno_task) for a task slug -- the F&O activity and the DevOps-linked task id."""
    if not slug:
        return "", ""
    for state in ("open", "in-progress", "done", "cancelled"):
        p = os.path.join(DEV_WORKSPACE, "ops", "tasks", state, slug + ".md")
        if os.path.exists(p):
            return _read_field(p, "activity") or "", _read_field(p, "fno_task") or ""
    return "", ""


# ---------- rendering ----------

def rows_for(heartbeats):
    """-> list of F&O rows {project, proj_id, activity, fno_task, hours, billable}, grouped by the
    finest dimension present: two task slugs that share an activity (both with no task) merge to the
    activity; distinct tasks stay separate; a slug with neither falls back to the project."""
    raw = {}   # (project, slug) -> raw active hours
    for (project, slug), ivs in group(heartbeats).items():
        if ivs:
            raw[(project, slug)] = stretch_hours(ivs)
    agg = {}   # (project, proj_id, activity, fno_task) -> summed hours
    for (project, slug), hrs in raw.items():
        activity, fno_task = task_dims(slug)
        key = (project, project_id(project), activity, fno_task)
        agg[key] = agg.get(key, 0.0) + hrs
    rows = []
    for (project, pid, activity, fno_task), hrs in agg.items():
        hours = max(round_quarter(hrs), MIN_HOURS)   # any work on a line that day counts as >= 0.5 h
        rows.append({"project": project, "proj_id": pid, "activity": activity,
                     "fno_task": fno_task, "hours": hours,
                     "billable": project.startswith("customers/")})
    rows.sort(key=lambda r: (not r["billable"], r["project"], r["activity"], r["fno_task"]))
    return rows


# ---------- full-day floor (README section 8) ----------

def load_absence():
    """ops/time/absence.md -> {date: {'kind','project','note'}}. Missing file = {}."""
    out = {}
    try:
        with open(ABSENCE, encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s.startswith("|"):
                    continue
                c = [x.strip() for x in s.strip("|").split("|")]
                if len(c) < 2 or not DATE_RE.match(c[0]):
                    continue
                kind = c[1].lower()
                if kind not in ABSENCE_KINDS:
                    continue
                out[c[0]] = {"kind": kind,
                             "project": c[2] if len(c) > 2 and c[2] != "-" else "",
                             "note": c[3] if len(c) > 3 and c[3] != "-" else ""}
    except Exception:
        pass
    return out


def is_workday(date):
    return datetime.date.fromisoformat(date).weekday() < 5


def day_active_hours(day_hbs):
    """Total active time across the whole day, all projects merged -- the 'did I work' measure."""
    return stretch_hours([(hb["start"], hb["end"]) for hb in day_hbs])


def apply_floor(rows, date, active_h, absence=None):
    """Lift a worked workday to FULL_DAY. Returns (rows, raw_total, claimed_total|None).

    The deficit is split PROPORTIONALLY across the day's BILLABLE lines (internal lines are left
    alone, so the floor never inflates non-billable hours); a day with no billable line splits it
    across whatever lines it has. Rounding drift lands on the largest line so the day totals exactly
    FULL_DAY. Weekends, absence days and days already at/over FULL_DAY are returned untouched."""
    raw = round(sum(r["hours"] for r in rows), 2)
    if not rows or not is_workday(date) or active_h < ACTIVE_TRIGGER:
        return rows, raw, None
    if absence and date in absence and absence[date]["kind"] != "offline":
        return rows, raw, None
    deficit = round_quarter(FULL_DAY - raw)
    if deficit <= 0:
        return rows, raw, None
    targets = [r for r in rows if r["billable"]] or rows
    base = sum(r["hours"] for r in targets)
    ordered = sorted(targets, key=lambda r: -r["hours"])
    rest = deficit
    for r in ordered[1:]:
        share = min(rest, round_quarter(deficit * r["hours"] / base)) if base else 0.0
        r["hours"] = round(r["hours"] + share, 2)
        rest = round(rest - share, 2)
    ordered[0]["hours"] = round(ordered[0]["hours"] + rest, 2)
    return rows, raw, round(raw + deficit, 2)


def offline_rows(project):
    """A full day on one project, for an 'offline' absence entry (worked, no keyboard)."""
    return [{"project": project, "proj_id": project_id(project), "activity": "", "fno_task": "",
             "hours": FULL_DAY, "billable": project.startswith("customers/")}]


def render_table(rows):
    lines = ["| Project | Proj ID | Activity | Task | Hours | Billable |",
             "|---|---|---|---|---|---|"]
    bill = intern_ = 0.0
    for r in rows:
        lines.append("| %s | %s | %s | %s | %.2f | %s |" % (
            r["project"], r["proj_id"], r["activity"] or "-", r["fno_task"] or "-",
            r["hours"], "yes" if r["billable"] else "no"))
        if r["billable"]:
            bill += r["hours"]
        else:
            intern_ += r["hours"]
    lines.append("")
    lines.append("**Billable total:** %.2f h" % bill)
    lines.append("**Internal total:** %.2f h" % intern_)
    return "\n".join(lines), bill, intern_


def write_daily(date, rows, note=""):
    os.makedirs(daily_dir(date), exist_ok=True)
    dow = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%a")
    table, _, _ = render_table(rows)
    body = ("# Timesheet - %s (%s)\n\n"
            "Generated by ops/time/rollup.py from heartbeats; reviewed/adjusted at /log.\n"
            "Rounded to 0.25 h, min 0.5 h. Edit this file to correct -- never the heartbeats. "
            "See ops/time/README.md.\n\n%s\n%s" % (date, dow, table, note))
    with open(daily_path(date), "w", encoding="utf-8") as f:
        f.write(body)


# ---------- by-date reports (read-only) ----------

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def week_key(date_str):
    iso = datetime.date.fromisoformat(date_str).isocalendar()
    return "%04d-W%02d" % (iso[0], iso[1])


def parse_daily_file(date):
    """Read a finalized timesheet/<date>.md back into rows (honours manual corrections).
    Returns the row list, or None if no file exists for that date."""
    path = daily_path(date)
    if not os.path.exists(path):
        return None
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s.startswith("|"):
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) != 6 or cells[0] == "Project" or set(cells[0]) <= set("-"):
                continue
            try:
                hours = float(cells[4])
            except ValueError:
                continue
            rows.append({"project": cells[0], "proj_id": cells[1],
                         "activity": "" if cells[2] == "-" else cells[2],
                         "fno_task": "" if cells[3] == "-" else cells[3],
                         "hours": hours, "billable": cells[5].lower() == "yes"})
    return rows


def known_dates(hbs):
    dates = set(hb["date"] for hb in hbs)
    # daily files live in timesheet/<YYYY-MM>/<date>.md
    for p in glob.glob(os.path.join(TIMESHEET, "*", "*.md")):
        name = os.path.basename(p)[:-3]
        if DATE_RE.match(name):
            dates.add(name)
    return dates


MERGE_THRESHOLD = 2.0   # a day-entry at/over this stays put; under it gets merged by week
DAY_CAP = 9.0           # a merged entry is never placed where it pushes a day over this


def consolidate_week(entries, period_dates, threshold=None):
    """Reduce small scattered entries. Any day-entry >= MERGE_THRESHOLD stays untouched. For each
    project, its sub-threshold day-entries within an ISO week are summed and placed on ONE day of
    that week, chosen so the day's total stays <= DAY_CAP. (Days already over the cap from untouched
    entries are not used as placement targets and are not redistributed.)

    `threshold` overrides MERGE_THRESHOLD for one call -- the F&O entry page passes a higher one to
    get the fewest possible lines to type. Callers that omit it (the /time reports) are unchanged."""
    thr = MERGE_THRESHOLD if threshold is None else threshold
    fixed = [e for e in entries if e["hours"] >= thr]
    small = [e for e in entries if e["hours"] < thr]
    day_total = {}
    for e in fixed:
        day_total[e["date"]] = day_total.get(e["date"], 0.0) + e["hours"]
    groups = {}
    for e in small:
        key = (week_key(e["date"]), e["project"], e["proj_id"], e["activity"],
               e["fno_task"], e["billable"])
        groups.setdefault(key, []).append(e)
    placed = []
    for key in sorted(groups):
        wk, project, pid, activity, fno_task, billable = key
        es = groups[key]
        total = round_quarter(sum(x["hours"] for x in es))
        own_days = sorted(set(x["date"] for x in es))               # days actually worked
        week_days = sorted(d for d in period_dates if week_key(d) == wk)
        order = own_days + [d for d in week_days if d not in own_days]
        live = any(x["live"] for x in es)
        row = lambda d, hrs: {"date": d, "project": project, "proj_id": pid, "activity": activity,
                              "fno_task": fno_task, "hours": hrs, "billable": billable,
                              "live": live}
        # Fill the FEWEST days that can hold the group, each up to DAY_CAP, preferring days the
        # line was actually worked. A group larger than the cap used to land whole on one day --
        # at MERGE_THRESHOLD 2.0 that was rare, but a caller passing a higher threshold sweeps in
        # bigger entries and could produce a 15 h day, which is not enterable.
        left = total
        for d in order:
            if left <= 0:
                break
            room = round_quarter(DAY_CAP - day_total.get(d, 0.0))
            if room <= 0:
                continue
            take = min(left, room)
            day_total[d] = day_total.get(d, 0.0) + take
            placed.append(row(d, take))
            left = round(left - take, 2)
        if left > 0:                      # every day in the week is at the cap -- keep the hours
            day_total[own_days[0]] = day_total.get(own_days[0], 0.0) + left
            placed.append(row(own_days[0], left))
    return fixed + placed


def render_entries(entries):
    entries = sorted(entries, key=lambda e: (e["date"], not e["billable"], e["project"],
                                             e["activity"], e["fno_task"]))
    lines = ["| Date | Project | Proj ID | Activity | Task | Hours | Billable |",
             "|---|---|---|---|---|---|---|"]
    bill = intern_ = 0.0
    live_dates, day_total = set(), {}
    for e in entries:
        if e["live"]:
            live_dates.add(e["date"])
        lines.append("| %s | %s | %s | %s | %s | %.2f | %s |" % (
            e["date"] + (" (live)" if e["live"] else ""), e["project"], e["proj_id"],
            e["activity"] or "-", e["fno_task"] or "-", e["hours"],
            "yes" if e["billable"] else "no"))
        day_total[e["date"]] = day_total.get(e["date"], 0.0) + e["hours"]
        if e["billable"]:
            bill += e["hours"]
        else:
            intern_ += e["hours"]
    print("\n".join(lines))
    print("\n**Billable total:** %.2f h" % bill)
    print("**Internal total:** %.2f h" % intern_)
    print("**Period total:** %.2f h" % (bill + intern_))
    over = sorted(d for d, h in day_total.items() if h > DAY_CAP + 1e-9)
    if over:
        print("\n(over 9 h/day from untouched >=2 h entries -- left as-is: %s)"
              % ", ".join("%s = %.2f h" % (d, day_total[d]) for d in over))
    if live_dates:
        print("\n(live = not yet finalized; run /time rollup to lock in: %s)"
              % ", ".join(sorted(live_dates)))


def report(hbs, today, kind, period, merge=False):
    """Print a by-date report for one week (kind='week') or month (kind='month').
    merge=True consolidates sub-2 h entries per project per week (see consolidate_week)."""
    hbs_by_date = {}
    for hb in hbs:
        hbs_by_date.setdefault(hb["date"], []).append(hb)
    if kind == "month":
        period = period or today[:7]
        in_range = lambda d: d[:7] == period
        title = "Month %s" % period
    else:
        period = period or week_key(today)
        try:
            yr, wk = int(period[:4]), int(period[6:])
            title = "Week %s (%s to %s)" % (
                period, datetime.date.fromisocalendar(yr, wk, 1),
                datetime.date.fromisocalendar(yr, wk, 7))
        except Exception:
            title = "Week %s" % period
        in_range = lambda d: week_key(d) == period

    entries, present_dates = [], []
    for d in sorted(x for x in known_dates(hbs) if in_range(x)):
        rows = parse_daily_file(d)
        live = rows is None
        if live:
            day_hbs = hbs_by_date.get(d, [])
            rows = rows_for(day_hbs)
            if d < today:   # today is still accruing -- the floor is only meaningful once closed
                rows, _, _ = apply_floor(rows, d, day_active_hours(day_hbs), load_absence())
        rows = [r for r in rows if r["hours"] > 0]
        if not rows:
            continue
        present_dates.append(d)
        for r in rows:
            entries.append({"date": d, "project": r["project"], "proj_id": r["proj_id"],
                            "activity": r["activity"], "fno_task": r["fno_task"],
                            "hours": r["hours"], "billable": r["billable"], "live": live})

    print("# %s -- by date%s\n" % (title, " (consolidated)" if merge else ""))
    if not entries:
        print("(no time recorded in this period)")
        return
    if merge:
        entries = consolidate_week(entries, present_dates)
    render_entries(entries)


# ---------- weekly coverage check (README section 8) ----------

def week_dates(period):
    yr, wk = int(period[:4]), int(period[6:])
    return [str(datetime.date.fromisocalendar(yr, wk, i)) for i in range(1, 8)]


def day_state(date, hbs_by_date, absence, today):
    """-> (status, hours, detail). status in future/absent/final/live/empty/weekend."""
    if date > today:
        return "future", 0.0, ""
    entry = absence.get(date)
    rows = parse_daily_file(date)
    day_hbs = hbs_by_date.get(date, [])
    if entry and entry["kind"] != "offline" and rows is None and not day_hbs:
        return "absent", 0.0, entry["kind"]
    if rows is not None:
        hrs = round(sum(r["hours"] for r in rows), 2)
        if entry and entry["kind"] != "offline":
            # tracked work on a day marked absent -- kept, unfloored, and flagged rather than dropped
            return "final", hrs, "marked %s but time was tracked -- check absence.md" % entry["kind"]
        return "final", hrs, ""
    if day_hbs:
        rows = rows_for(day_hbs)
        active = day_active_hours(day_hbs)
        rows, raw, claimed = apply_floor(rows, date, active, absence)
        return "live", (claimed if claimed is not None else raw), (
            "floor -> %.2f h" % claimed if claimed is not None else "")
    if date in absence and absence[date]["kind"] == "offline":
        return "live", FULL_DAY, "offline, from absence.md"
    return ("empty" if is_workday(date) else "weekend"), 0.0, ""


def check(hbs, today, period=None):
    """Per-week coverage against the full-day rule. Reports unaccounted workdays and the running
    month total. Writes nothing -- the floor itself is applied by finalize()."""
    hbs_by_date = {}
    for hb in hbs:
        hbs_by_date.setdefault(hb["date"], []).append(hb)
    absence = load_absence()
    cur = week_key(today)
    if period:
        periods = [period]
    else:
        prev = week_key(str(datetime.date.fromisoformat(today) - datetime.timedelta(days=7)))
        periods = [prev, cur]

    unaccounted, under = [], []
    for wk in periods:
        dates = week_dates(wk)
        print("# Week %s coverage (%s to %s)\n" % (wk, dates[0], dates[6]))
        lines = ["| Date | Day | Status | Hours | Note |", "|---|---|---|---|---|"]
        worked = target = 0.0
        for d in dates:
            status, hrs, detail = day_state(d, hbs_by_date, absence, today)
            if status == "weekend" and hrs == 0.0:
                continue
            if status == "future":
                continue
            off = d in absence and absence[d]["kind"] != "offline"
            if is_workday(d) and not off:
                target += FULL_DAY
            worked += hrs
            if status == "empty":
                unaccounted.append(d)
                detail = "no keyboard time and no absence entry"
            if status == "final" and is_workday(d) and not off and 0 < hrs < FULL_DAY:
                under.append((d, hrs))
                detail = "finalized below the floor -- edit the daily file to lift it"
            dow = datetime.date.fromisoformat(d).strftime("%a")
            lines.append("| %s | %s | %s | %s | %s |" % (
                d, dow, status, "-" if status in ("empty", "absent") else "%.2f" % hrs,
                detail or "-"))
        print("\n".join(lines))
        print("\n**Week total:** %.2f h of %.2f h target (%.0f%%)"
              % (worked, target, (100.0 * worked / target) if target else 0.0))
        if worked + 1e-9 < target:
            print("**Short by %.2f h.**" % (target - worked))
        print("")

    # month-to-date against the guarantee: 7.5 h x elapsed workdays, minus absence.
    # Scoped to the month of the LAST week checked, so `--check <old week>` reports that month.
    ym = week_dates(periods[-1])[0][:7]
    d = datetime.date.fromisoformat(ym + "-01")
    m_target = m_worked = 0.0
    while str(d)[:7] == ym and str(d) <= today:
        ds = str(d)
        status, hrs, _ = day_state(ds, hbs_by_date, absence, today)
        if is_workday(ds) and not (ds in absence and absence[ds]["kind"] != "offline"):
            m_target += FULL_DAY
        m_worked += hrs
        d += datetime.timedelta(days=1)
    print("**Month %s to date:** %.2f h of %.2f h target (%.0f%%)"
          % (ym, m_worked, m_target, (100.0 * m_worked / m_target) if m_target else 0.0))

    if unaccounted:
        print("\n## Unaccounted workdays -- ANSWER THESE\n")
        for d in unaccounted:
            print("  %s (%s)" % (d, datetime.date.fromisoformat(d).strftime("%a")))
        print("\nAdd a row to ops/time/absence.md for each:")
        print("  | <date> | vacation \\| holiday \\| sick \\| offline | <project if offline> | <note> |")
        print("An 'offline' row with a project is claimed as a full day at the next rollup.")
    if under:
        print("\n## Finalized below the floor (not changed automatically)\n")
        for d, h in under:
            print("  %s  %.2f h  (+%.2f h to reach %.2f)" % (d, h, FULL_DAY - h, FULL_DAY))


def flag_value(flag):
    """Return the value after `flag`, '' if the flag is present without a value, or None if absent."""
    if flag in sys.argv:
        i = sys.argv.index(flag)
        if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith("-"):
            return sys.argv[i + 1]
        return ""
    return None


# ---------- modes ----------

def finalize(hbs, today):
    """Write a timesheet for every complete past day with heartbeats but no timesheet yet, and for
    every past 'offline' absence day. The full-day floor (section 8) is applied as it writes."""
    by_date = {}
    for hb in hbs:
        by_date.setdefault(hb["date"], []).append(hb)
    absence = load_absence()
    written = []
    for date in sorted(set(by_date) | set(absence)):
        if date >= today:
            continue  # today is still accruing -- only previewed
        if os.path.exists(daily_path(date)):
            continue  # already finalized
        day_hbs = by_date.get(date, [])
        entry = absence.get(date)
        if entry and entry["kind"] != "offline" and not day_hbs:
            continue  # vacation/holiday/sick with nothing tracked -- no timesheet at all
        if entry and entry["kind"] == "offline" and not day_hbs:
            if not entry["project"]:
                continue  # offline day with no project named -- cannot attribute; check reports it
            write_daily(date, offline_rows(entry["project"]),
                        "\n> Full-day floor: offline day (no keyboard time), claimed %.2f h "
                        "from ops/time/absence.md.\n" % FULL_DAY)
            written.append(date)
            continue
        rows = rows_for(day_hbs)
        if not rows:
            continue
        rows, raw, claimed = apply_floor(rows, date, day_active_hours(day_hbs), absence)
        note = ""
        if claimed is not None:
            note = ("\n> Full-day floor: %.2f h measured -> %.2f h claimed (worked workday). "
                    "See ops/time/README.md section 8 and ops/time/value/%s.md.\n"
                    % (raw, claimed, date))
        write_daily(date, rows, note)
        written.append(date)
    return written


def preview(hbs, today):
    day_hbs = [h for h in hbs if h["date"] == today]
    day_rows = rows_for(day_hbs)
    print("Today (%s) -- live, not finalized:\n" % today)
    print(render_table(day_rows)[0] if day_rows else "  (no time tracked yet today)")
    if day_rows and is_workday(today):
        raw = sum(r["hours"] for r in day_rows)
        if day_active_hours(day_hbs) >= ACTIVE_TRIGGER and raw < FULL_DAY:
            print("\n(full-day floor at finalize: %.2f h -> %.2f h, +%.2f h onto the billable "
                  "lines -- see README section 8)" % (raw, FULL_DAY, FULL_DAY - raw))


def main():
    hbs = load_heartbeats()
    today = to_local(datetime.datetime.now(datetime.timezone.utc)).strftime("%Y-%m-%d")
    if "--preview" in sys.argv:
        preview(hbs, today)
        return
    merge = "--merge" in sys.argv
    wk = flag_value("--week")
    if wk is not None:
        report(hbs, today, "week", wk or None, merge)
        return
    mo = flag_value("--month")
    if mo is not None:
        report(hbs, today, "month", mo or None, merge)
        return
    ck = flag_value("--check")
    if ck is not None:
        check(hbs, today, ck or None)
        return
    written = finalize(hbs, today)
    if written:
        print("Finalized days: " + ", ".join(written))
    else:
        print("No new days to finalize.")
    print("")
    check(hbs, today)   # the weekly coverage check runs with every rollup (README section 8)


if __name__ == "__main__":
    main()
