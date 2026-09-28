#!/usr/bin/env python
"""Workspace dashboard -- a derive-only view over the workspace's own substrate.

Reads (never writes) the existing sources of truth:
  ops/tasks/<state>/*.md      the cross-project task queue
  ops/time/heartbeats + timesheet  tracked hours (via ops/time/rollup.py -- the 15+5 model)
  <project>/CLAUDE.md         the Identity block (fno_code, status, type, focus)
  <project>/CONTEXT.md        Current Focus / State / Next Actions / Open Threads
  customers/<C>/CLAUDE.md     the customer node (profile + project index)
  ops/TODO.md                 unprocessed capture

Nothing here is a new source of truth (Guardrail 7): delete this file and no knowledge is lost.

Modes:
  python ops/dashboard.py            serve at http://127.0.0.1:8787 and open a browser
  python ops/dashboard.py --json     print the collected payload; write nothing
  python ops/dashboard.py --no-open  serve without opening a browser

Three pages, all under ops/web/ (Preact + htm, no build step -- see web/vendor/README.md):
  /           the day: triage, tasks in progress, what moved (from /api/today = bin/daybrief.py)
  /projects   every project ranked by activity, and the customers above them
  /time       what goes into F&O -- the entry blocks per company, the readiness gate, the
              week's evidence, and Excel
Each re-fetches on load, on Refresh and on a timer, so nothing on screen is stale.

Write paths (the page never edits a file itself):
  /api/launch     start a session or a VS Code window rooted at a project -- which is also
                  what makes that session's time attribute to the right project
  /api/task       mechanical task moves; /api/todo ticks a capture
  /api/reassign   move a Dev timesheet line to the project it was really for
  /api/timesheet  correct one line of a finalized day (ops/time/README.md: edit the file)
  /api/tssplit    split one such line between the work sessions behind it
  /api/fno        set an F&O field on a project's ## Identity or a customer's ## Customer
  /api/xlsx       the visible entry rows as a workbook

Pure stdlib, ASCII-only (workspace convention).
"""
import os, sys, re, json, glob, datetime, subprocess, shutil, importlib.util
import io, time, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.substrate import (read, frontmatter, identity, sections, bullets,
                           labelled, field, plain, first_para, days_ago)
from lib.workspace import customer_dirs, project_dirs, customer_name
from lib import fno
from lib import lines as linedesc
from lib import attribution
from lib import noinvoice
from lib import fnotasks
from lib import sessionlines

ROOT = os.environ.get("DEV_WORKSPACE", r"C:\Dev")
HERE = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get("DASHBOARD_PORT", "8787"))

# Freshness buckets (days since a project was last worked) -> status role in the palette.
FRESH_GOOD, FRESH_WARN, FRESH_SERIOUS = 7, 21, 60

# Consolidation threshold for the F&O ENTRY PAGE only: any day-entry below this is merged into one
# day per ISO week per F&O line, so there are as few lines to type as possible. Higher than
# rollup.MERGE_THRESHOLD (2.0), which the /time reports keep -- this view exists to be typed into
# F&O, not to describe how the days actually ran. rollup.DAY_CAP still bounds where a merge lands.
ENTRY_MERGE_THRESHOLD = 5.0


# ---------- rollup reuse (the 15+5 model lives there; do not reimplement) ----------

def _load_rollup():
    path = os.path.join(ROOT, "ops", "time", "rollup.py")
    spec = importlib.util.spec_from_file_location("rollup", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rollup = _load_rollup()


_daybrief_mod = None


def _daybrief():
    """ops/bin/daybrief.py, loaded on demand so a fault there never stops the server.

    Memoised after the first success: /api/today and the project table both want it, and
    re-executing the module per request costs a full parse. A failed load leaves the memo
    empty, so the next call retries."""
    global _daybrief_mod
    if _daybrief_mod is None:
        path = os.path.join(ROOT, "ops", "bin", "daybrief.py")
        spec = importlib.util.spec_from_file_location("daybrief", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _daybrief_mod = mod
    return _daybrief_mod


def _daybrief_model():
    """The day-brief model, or {} if it cannot be built.

    The project table borrows the resume-card fields from here rather than parsing the
    cards a second time. A fault in the brief must not take the dashboard down with it."""
    try:
        return _daybrief().build()
    except Exception:
        return {}


# ---------- discovery ----------

def discover():
    """-> (projects, customers). A project is a folder with its own CLAUDE.md."""
    projects, customers = {}, {}

    for cname, cdir in customer_dirs(ROOT):
        ctext = read(os.path.join(cdir, "CLAUDE.md"))
        cctx = sections(read(os.path.join(cdir, "CONTEXT.md")))
        prof = {}
        cust_block = sections(ctext).get("Customer", "")
        for line in cust_block.splitlines():
            m = re.match(r"^([a-z_]+):(.*)$", line.strip())
            if m:
                prof[m.group(1)] = plain(m.group(2))
        customers[cname] = {
            "key": "customers/" + cname, "name": cname, "path": cdir,
            "status": prof.get("status", ""), "language": prof.get("language", ""),
            "contacts": prof.get("contacts", ""), "infra": prof.get("infra", ""),
            "about": first_para(sections(ctext).get("About", "")),
            "focus": first_para(cctx.get("Current Focus", "")),
            "projects": [],
        }
        for key, pdir in project_dirs(ROOT, cname):
            projects[key] = build_project(key, pdir, cname)
            customers[cname]["projects"].append(key)

    for key, pdir in project_dirs(ROOT, "own"):
        projects[key] = build_project(key, pdir, None)

    projects["Dev"] = {
        "key": "Dev", "name": "Dev (workspace itself)", "customer": None, "path": ROOT,
        "billable": False, "fno_code": "INTERNAL-RND", "type": "workspace", "focus_tag": "",
        "status": "active", "ctx_status": "active", "last_worked": "",
        "focus": first_para(sections(read(os.path.join(ROOT, "CONTEXT.md"))).get("Current Focus", ""))
                 or "The workspace itself -- agents, skills, hooks, memory, time tracking.",
        "next_actions": [], "open_threads": [], "in_progress": [], "blocked_on": [],
    }
    return projects, customers


def build_project(key, pdir, customer):
    ident = identity(read(os.path.join(pdir, "CLAUDE.md")))
    ctx = sections(read(os.path.join(pdir, "CONTEXT.md")))
    state = ctx.get("State", "")
    return {
        "key": key, "name": os.path.basename(pdir), "customer": customer, "path": pdir,
        "billable": key.startswith("customers/"),
        "fno_code": ident.get("fno_code", "") or "UNSET",
        "fno_description": ident.get("fno_description", ""),
        "type": ident.get("type", ""), "focus_tag": ident.get("focus", ""),
        "status": ident.get("status", ""),
        "ctx_status": plain(field(state, "Status")) or ident.get("status", ""),
        "last_worked": (field(state, "Last worked") or "")[:10],
        "focus": first_para(ctx.get("Current Focus", "")),
        "next_actions": bullets(ctx.get("Next Actions", "")),
        "open_threads": bullets(ctx.get("Open Threads", "")),
        "in_progress": labelled(state, "In progress"),
        "blocked_on": labelled(state, "Blocked on"),
    }


# ---------- tasks ----------

def collect_tasks():
    out = []
    for state in ("in-progress", "open", "done", "cancelled"):
        for path in sorted(glob.glob(os.path.join(ROOT, "ops", "tasks", state, "*.md"))):
            text = read(path)
            fm, _ = frontmatter(text)
            body = sections(text)
            log = bullets(body.get("Log", ""), limit=50)
            out.append({
                "slug": os.path.basename(path)[:-3], "state": state, "path": path,
                "title": fm.get("title", "") or os.path.basename(path)[:-3],
                "project": fm.get("project", ""), "owner": fm.get("owner", ""),
                "priority": fm.get("priority", "normal"), "source": fm.get("source", ""),
                "activity": fm.get("activity", ""), "fno_task": fm.get("fno_task", ""),
                "blocked_by": fm.get("blocked_by", ""), "created": fm.get("created", ""),
                "what": first_para(body.get("What", ""), 900),
                "why": first_para(body.get("Why", ""), 600),
                "context": bullets(body.get("Context", ""), limit=8),
                "log": log[-12:], "log_last": (log[-1][:10] if log else ""),
            })
    return out


# ---------- time ----------

def collect_time(today):
    """-> (entries, unfinalized_dates). One entry per date/project/dimension, timesheet-first."""
    hbs = rollup.load_heartbeats()
    by_date = {}
    for hb in hbs:
        by_date.setdefault(hb["date"], []).append(hb)
    entries, unfinalized = [], []
    for d in sorted(rollup.known_dates(hbs)):
        rows = rollup.parse_daily_file(d)
        live = rows is None
        if live:
            rows = rollup.rows_for(by_date.get(d, []))
            if d < today and rows:
                unfinalized.append(d)
        for r in rows or []:
            if r["hours"] <= 0:
                continue
            entries.append({"date": d, "project": r["project"], "proj_id": r["proj_id"],
                            "activity": r["activity"], "fno_task": r["fno_task"],
                            "hours": r["hours"], "billable": r["billable"], "live": live})
    return entries, unfinalized


# ---------- week audit (the timesheet page: every category, one week at a time) ----------
# The entry page (collect_entry) answers "what do I type into F&O". This answers "is the week
# whole, and what is behind each number" -- measured vs target vs the weighted hours from the
# value model, per ADR-005 v2. Derive-only: rollup owns the hours, ops/time/value/ the evidence.

AUDIT_WEEKS = 8          # floor: the page always offers at least this many ISO weeks back
VALUE = os.path.join(ROOT, "ops", "time", "value")
TIER_NAME = {"1": "T1", "2": "T2", "3": "T3", "4": "T4", "5": "T5"}


def _value_lines(date):
    """Per F&O line evidence from ops/time/value/<date>.jsonl -- [] if the day was never derived."""
    path = os.path.join(VALUE, date + ".jsonl")
    out = []
    if not os.path.exists(path):
        return out
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    out.append(json.loads(line))
    except Exception:
        return []
    return out


def _dimkey(project, activity, fno_task):
    return "%s|%s|%s" % (project, activity or "", fno_task or "")


def _blank_agg():
    return {"keyboard": 0.0, "weighted": 0.0, "turns": 0, "stretches": 0,
            "t5": 0, "tiers": {}, "files": set()}


def _fold(a, v):
    """Fold one value/<date>.jsonl record into an aggregate."""
    a["keyboard"] += v.get("keyboard_h") or 0.0
    a["weighted"] += v.get("weighted_h") or 0.0
    a["turns"] += v.get("turns") or 0
    a["stretches"] += v.get("stretches") or 0
    a["t5"] += v.get("t5_events") or 0
    for t, tv in (v.get("tiers") or {}).items():
        n = TIER_NAME.get(t, t)
        a["tiers"][n] = round(a["tiers"].get(n, 0.0) + (tv.get("minutes") or 0.0), 1)
    for dv in (v.get("deliverables") or []):
        a["files"].add(dv["path"])
    return a


def _scale_agg(a, f):
    """A fraction of an aggregate. Hours divide; so do the counts, on purpose -- keeping the
    same turns-per-hour density across a split is the most neutral thing to do with them,
    and that density is what decides where in the band the line sits."""
    return {"keyboard": a["keyboard"] * f, "weighted": a["weighted"] * f,
            "turns": int(round(a["turns"] * f)), "stretches": int(round(a["stretches"] * f)),
            "t5": int(round(a["t5"] * f)),
            "tiers": {k: round(v * f, 1) for k, v in a["tiers"].items()},
            "files": a["files"]}


def _merge_agg(a, b):
    a["keyboard"] += b["keyboard"]
    a["weighted"] += b["weighted"]
    a["turns"] += b["turns"]
    a["stretches"] += b["stretches"]
    a["t5"] += b["t5"]
    for k, v in b["tiers"].items():
        a["tiers"][k] = round(a["tiers"].get(k, 0.0) + v, 1)
    a["files"] = set(a["files"]) | set(b["files"])
    return a


def _weights(slots, keys):
    """How to split something across a project's lines for one date: by registered hours,
    equally when none of them registered any."""
    tot = sum(slots[k]["row"]["hours"] for k in keys)
    if tot > 0:
        return [(k, slots[k]["row"]["hours"] / tot) for k in keys]
    return [(k, 1.0 / len(keys)) for k in keys]


def line_rows(date, sheet, measured_rows, values):
    """One date's F&O lines: the timesheet row, with the measurement and the evidence.

    Three sources, keyed three ways:

      `sheet`          the finalized timesheet -- authoritative, because it is what gets
                       typed into F&O and because /log corrects it BY HAND. None when the
                       day is not finalized, in which case `measured_rows` stands in.
      `measured_rows`  the 15+5 model recomputed from the heartbeats, keyed on the task
                       file's dimensions as they are NOW.
      `values`         the value records, keyed on the dimensions as they were derived.

    A correction at /log moves the timesheet's key and leaves the other two behind. That
    showed as two half-lines -- one with hours and no measurement, one with the measurement
    and no hours -- which is what made a line read `Measured 0` beside a real F&O entry
    (2026-09-07 Matas: Task-65904 on the sheet, Task-65905 everywhere else).

    So: match on the exact key; attach what is left over to the same PROJECT on that date,
    split across its lines in proportion to their registered hours -- the same rule the
    entry page uses to spread a dimension's hours -- and mark those lines `shared`, because
    the number is then a share of the project's day and not the line's own. Evidence for a
    project with NO registered line that date keeps a line of its own: that is work measured
    and registered somewhere else, and inventing an owner for it would be worse than showing
    it.

    Hours are conserved: every measured hour lands on exactly one line."""
    sheet_rows = sheet if sheet is not None else measured_rows
    slots = {}
    for r in sheet_rows:
        slots[_dimkey(r["project"], r["activity"], r["fno_task"])] = {
            "row": r, "meas": 0.0, "agg": _blank_agg(), "shared": False}

    meas_by = {}
    for r in measured_rows:
        k = _dimkey(r["project"], r["activity"], r["fno_task"])
        meas_by[k] = round(meas_by.get(k, 0.0) + r["hours"], 2)
    agg_by = {}
    for v in values:
        _fold(agg_by.setdefault(_dimkey(v["project"], v.get("activity"), v.get("fno_task")),
                                _blank_agg()), v)

    for k in list(meas_by):
        if k in slots:
            slots[k]["meas"] = meas_by.pop(k)
    for k in list(agg_by):
        if k in slots:
            _merge_agg(slots[k]["agg"], agg_by.pop(k))

    by_proj = {}
    for k in slots:
        by_proj.setdefault(k.split("|", 1)[0], []).append(k)
    for k in list(meas_by):
        keys = by_proj.get(k.split("|", 1)[0])
        if not keys:
            continue
        for kk, f in _weights(slots, keys):
            slots[kk]["meas"] = round(slots[kk]["meas"] + meas_by[k] * f, 2)
            slots[kk]["shared"] = True
        meas_by.pop(k)
    for k in list(agg_by):
        keys = by_proj.get(k.split("|", 1)[0])
        if not keys:
            continue
        for kk, f in _weights(slots, keys):
            _merge_agg(slots[kk]["agg"], _scale_agg(agg_by[k], f))
            slots[kk]["shared"] = True
        agg_by.pop(k)

    # A project with no line that date whose CUSTOMER has one was moved between that
    # customer's projects at /log (2026-09-12 Aeven: ServiceNowPOC -> AtomicServiceNow; a
    # datahub line moved to the Carl Ras node). The measurement follows the move, spread
    # the same way. Across customers nothing is inferred.
    def cust(k):
        p = k.split("|", 1)[0].split("/")
        return "/".join(p[:2]) if p[0] == "customers" and len(p) > 1 else None
    by_cust = {}
    for k in slots:
        if cust(k):
            by_cust.setdefault(cust(k), []).append(k)
    for src in (meas_by, agg_by):
        for k in list(src):
            keys = by_cust.get(cust(k)) if cust(k) else None
            if not keys:
                continue
            for kk, f in _weights(slots, keys):
                if src is meas_by:
                    slots[kk]["meas"] = round(slots[kk]["meas"] + src[k] * f, 2)
                else:
                    _merge_agg(slots[kk]["agg"], _scale_agg(src[k], f))
                slots[kk]["shared"] = True
            src.pop(k)

    # Whatever is still homeless is work measured on a project with no registered line that
    # date -- reassigned at /log, usually. There is no timesheet dimension to preserve, so
    # one line per project says it once instead of once per stale key.
    left = {}
    for k in sorted(set(meas_by) | set(agg_by)):
        home = left.setdefault(k.split("|", 1)[0],
                               {"key": k, "meas": 0.0, "agg": _blank_agg(), "best": -1.0})
        home["meas"] = round(home["meas"] + meas_by.get(k, 0.0), 2)
        _merge_agg(home["agg"], agg_by.get(k) or _blank_agg())
        if meas_by.get(k, 0.0) > home["best"]:
            home["best"], home["key"] = meas_by.get(k, 0.0), k
    for home in left.values():
        slots[home["key"]] = {"row": None, "meas": home["meas"], "agg": home["agg"],
                              "shared": False}

    out = []
    for k in sorted(slots):
        s = slots[k]
        r, a = s["row"], s["agg"]
        project, activity, fno_task = k.split("|", 2)
        out.append({
            "date": date, "project": project, "activity": activity, "fno_task": fno_task,
            "proj_id": r["proj_id"] if r else rollup.project_id(project),
            "billable": r["billable"] if r else project.startswith("customers/"),
            "claimed": r["hours"] if r else 0.0,
            "measured": round(s["meas"], 2),
            "keyboard": round(a["keyboard"], 2), "weighted": round(a["weighted"], 2),
            "turns": a["turns"], "stretches": a["stretches"], "t5": a["t5"],
            "tiers": a["tiers"], "files": len(a["files"]),
            "topFiles": [os.path.basename(x) for x in sorted(a["files"])[:4]],
            "shared": s["shared"],
            "live": sheet is None,
        })
    return out


def audit_mondays(today):
    """Mondays of the ISO weeks the week page offers, newest first.

    Far enough back to reach the FIRST DAY OF LAST MONTH: the page's month filter offers 'last
    month' for exactly the case where entry is late, and that is worthless if the month's opening
    weeks are missing. A fixed count cannot do it -- the distance to the 1st of last month runs
    from ~5 weeks (early in a month) to ~10 (at month end)."""
    cur = datetime.date.fromisoformat(today)
    monday = cur - datetime.timedelta(days=cur.weekday())
    prev_first = (cur.replace(day=1) - datetime.timedelta(days=1)).replace(day=1)
    first_monday = prev_first - datetime.timedelta(days=prev_first.weekday())
    n = max(AUDIT_WEEKS, (monday - first_monday).days // 7 + 1)
    return [monday - datetime.timedelta(days=7 * back) for back in range(n)]


def collect_audit(today):
    """-> {weeks: [...], byWeek: {wk: {...}}} -- one fully-categorised block per ISO week."""
    hbs = rollup.load_heartbeats()
    hbs_by_date = {}
    for hb in hbs:
        hbs_by_date.setdefault(hb["date"], []).append(hb)
    absence = rollup.load_absence()

    weeks, by_week = [], {}
    for m in audit_mondays(today):
        iso = m.isocalendar()
        wk = "%04d-W%02d" % (iso[0], iso[1])
        weeks.append(wk)
        by_week[wk] = _audit_week(wk, hbs_by_date, absence, today)
    return {"weeks": weeks, "byWeek": by_week,
            "fullDay": rollup.FULL_DAY, "dayCap": rollup.DAY_CAP}


def _audit_week(wk, hbs_by_date, absence, today):
    dates = rollup.week_dates(wk)
    days, lines, spill = [], [], []
    target = 0.0
    for d in dates:
        if d > today:
            continue
        dh = hbs_by_date.get(d, [])
        entry = absence.get(d)
        off = bool(entry) and entry["kind"] != "offline"
        status, claimed, detail = rollup.day_state(d, hbs_by_date, absence, today)
        if status == "future":
            continue
        if d == today and status in ("empty", "weekend"):
            status = "today"      # still running -- not an unanswered day
        measured = round(sum(r["hours"] for r in rollup.rows_for(dh)), 2)
        wb, wi = rollup.weighted_hours(d)
        vals = _value_lines(d)

        day_agg = _blank_agg()
        for v in vals:
            _fold(day_agg, v)
            if v.get("spilled_from"):
                spill.append({"date": d, "project": v["project"],
                              "activity": v.get("activity") or "",
                              "hours": v.get("weighted_h") or 0.0, "from": v["spilled_from"]})
        workday = rollup.is_workday(d)
        # A day still running cannot be judged short, so it is not in the target yet. It joins
        # tomorrow, which is also when its heartbeats are complete enough to mean anything.
        day_target = 0.0 if (d == today or not workday or off) else rollup.FULL_DAY
        target += day_target
        days.append({
            "date": d, "dow": datetime.date.fromisoformat(d).strftime("%a"),
            "status": status, "detail": detail, "workday": workday,
            "absence": entry["kind"] if entry else None,
            "measured": measured, "claimed": claimed,
            "topup": round(claimed - measured, 2),
            "keyboard": round(day_agg["keyboard"], 2),
            "weighted": round((wb or 0.0) + (wi or 0.0), 2),
            "weightedBillable": wb, "weightedInternal": wi,
            "turns": day_agg["turns"], "stretches": day_agg["stretches"],
            "t5": day_agg["t5"], "tiers": day_agg["tiers"], "files": len(day_agg["files"]),
            "target": day_target,
            "short": round(max(0.0, day_target - claimed), 2),
        })

        # One date's F&O lines, joined from the three sources (see line_rows).
        lines.extend(line_rows(d, rollup.parse_daily_file(d), rollup.rows_for(dh), vals))

    tot = lambda f: round(sum(x[f] for x in days), 2)
    claimed = tot("claimed")
    return {
        "week": wk, "start": dates[0], "friday": dates[4], "end": dates[6],
        "running": any(x["date"] == today for x in days),
        "days": days, "lines": lines, "spill": spill,
        "target": round(target, 2),
        "totals": {
            "keyboard": tot("keyboard"), "measured": tot("measured"), "claimed": claimed,
            "weighted": tot("weighted"),
            "turns": sum(x["turns"] for x in days),
            "stretches": sum(x["stretches"] for x in days),
            "t5": sum(x["t5"] for x in days),
            "billable": round(sum(l["claimed"] for l in lines if l["billable"]), 2),
            "internal": round(sum(l["claimed"] for l in lines if not l["billable"]), 2),
            "coverage": round(100.0 * claimed / target, 1) if target else None,
            "short": round(max(0.0, target - claimed), 2),
        },
        "exceptions": {
            "under": [{"date": x["date"], "claimed": x["claimed"], "short": x["short"],
                       "weighted": x["weightedBillable"]}
                      for x in days if x["target"] and 0 < x["claimed"] < x["target"]],
            "unaccounted": [x["date"] for x in days if x["status"] == "empty"],
            "unfinalized": [x["date"] for x in days
                            if x["status"] == "live" and x["date"] < today],
            "overCap": [x["date"] for x in days if x["claimed"] > rollup.DAY_CAP],
        },
    }


def _command_openers():
    """First-40-chars of every slash command's description, lowercased.

    The turn hook records a slash command's expanded BODY as the User line (recurring defect,
    memory `capture-turn-records-expanded-help`), so `/switch-task` shows up as "Switch (or set)
    the time-tracking task for...". That is the command's help text, not what the session was
    about, and it crowds out the real turns. Matching against the command files themselves keeps
    the filter exact -- no guessing at what documentation prose looks like."""
    out = set()
    for path in glob.glob(os.path.join(ROOT, ".claude", "commands", "*.md")):
        head = plain((read(path) or "").strip().split("\n", 1)[0])
        if len(head) >= 20:
            out.add(head[:40].lower())
    return out


def memory_index():
    """{session8: [(yyyymmdd, first-user-line), ...]} from ops/memory/daily/.

    The turn-hook writes `id: <utc-ts>Z-<session8>` above each record, which is the only join
    between a heartbeat and what was actually being said in it."""
    idx, openers = {}, _command_openers()
    pat = re.compile(
        r"id: (\d{8})T\d{6}Z-([0-9a-f]{6,12})\n.*?\n---\n\n\*\*User:\*\* (.*?)\n", re.S)
    for path in sorted(glob.glob(os.path.join(ROOT, "ops", "memory", "daily", "*.md"))):
        for day, sess, line in pat.findall(read(path)):
            txt = plain(line)
            # Skip harness noise (~10% of turns): a skill's injected preamble, a background-task
            # notification, raw tool output echoed back. None of it says what the work WAS.
            if (not txt or txt.startswith("Base directory for this skill")
                    or txt.startswith("<") or "task-notification" in txt[:40]
                    or txt[:40].lower() in openers):
                continue
            idx.setdefault(sess, []).append((day, txt[:220]))
    return idx


# ---------- what a line was about (hover evidence) ----------
# A timesheet line says "Carl-Ras / - / -" and nothing more: the rollup deliberately does not
# group by session (that would fragment stretches and add a buffer + floor per session), and the
# finalized file carries no session id at all. So the line cannot answer "what was this?" --
# which is worst exactly where it matters, on a line with no activity and no task.
# This rebuilds the join from the heartbeats, which DO carry the session, and pairs it with the
# turn text the memory hook wrote for that session. Derive-only; never a billing number.

SESSION_WEEKS = 10       # how far back line evidence is carried in the payload
MIN_TURN_CHARS = 15      # "yes", "push", "do that" -- a turn this short describes nothing
TIP_LINES = 3            # turns shown per session in a hover
TIP_BLOCKS = 6           # sessions carried per line before the page says "+N more".
                         # Enough to split a day's line between all of them: one line has
                         # ever had more than four sessions behind it.


def _says_something(text):
    """A turn worth showing in a hover: long enough, and actually words.

    A markdown rule ("---------") or a row of dashes clears a length test but says nothing."""
    return (len(text) >= MIN_TURN_CHARS
            and sum(c.isalnum() for c in text) >= 8)


def collect_line_sessions(today):
    """{'<date>|<project>|<activity>|<task>': [{session, turns, hours, from, to, task, lines[]}]}
    (lowercased key).

    A session that has been SPLIT onto a line of its own is keyed under the dimensions it
    was split to, not the ones its work-task carries (ops/lib/sessionlines.py). The
    heartbeats are immutable, so without that both halves of a split line would go on
    showing all of the day's sessions -- which is the thing the split was for."""
    cutoff = str(datetime.date.fromisoformat(today) - datetime.timedelta(weeks=SESSION_WEEKS))
    mem = memory_index()
    marks = sessionlines.assigned()
    by = {}
    for hb in rollup.load_heartbeats():
        if hb["date"] < cutoff:
            continue
        activity, fno_task = rollup.task_dims(hb.get("task"))
        split = marks.get((hb["date"], hb.get("session") or "", hb["project"].lower()))
        if split:
            activity, fno_task = split["activity"], split["fno_task"]
        key = ("%s|%s|%s|%s" % (hb["date"], hb["project"], activity, fno_task)).lower()
        by.setdefault(key, {}).setdefault(hb.get("session") or "", []).append(hb)

    out = {}
    for key, sess_map in by.items():
        date = key.split("|", 1)[0]
        blocks = []
        for sess, group in sess_map.items():
            turns = mem.get(sess, [])
            # Prefer what was said on THIS date; a session spanning days would otherwise
            # describe the line with another day's work.
            same = [t for d, t in turns if d == date.replace("-", "")]
            picked = [t for t in (same or [t for _, t in turns]) if _says_something(t)]
            lines = list(dict.fromkeys(picked))[:TIP_LINES]
            slugs = sorted({hb["task"] for hb in group if hb.get("task")})
            # When it ran, so the sessions behind a line read in the order they
            # happened -- which is how you recognise which was which.
            span = [rollup.to_local(hb["start"]) for hb in group]
            blocks.append({
                "session": sess or "(no session id)",
                "turns": len(group),
                "from": min(span).strftime("%H:%M"),
                "to": max(rollup.to_local(hb["end"]) for hb in group).strftime("%H:%M"),
                "hours": round(sum(r["hours"] for r in rollup.rows_for(group)), 2),
                "task": slugs[0] if len(slugs) == 1 else ("; ".join(slugs) if slugs else ""),
                "lines": lines,
            })
        # A summary, not a transcript: the biggest sessions are the ones kept, and the
        # rest are counted. What is kept then reads in the order it happened.
        blocks.sort(key=lambda b: -b["hours"])
        keep = sorted(blocks[:TIP_BLOCKS], key=lambda b: b["from"])
        out[key] = {"blocks": keep, "total": len(blocks),
                    "more": max(0, len(blocks) - TIP_BLOCKS)}
    return out


def collect_internal(canon):
    """Internal (Dev + own/) time joined to its session, co-worked projects and turn text.

    Heartbeat-derived on purpose: the finalized timesheet is the billing truth but carries no
    session id, so it cannot answer 'what was this time actually about'. Splitting per session
    also fragments stretches -- each fragment earns its own 5 min buffer and 0.5 h floor -- so
    these hours run HIGHER than the timesheet and are a triage signal, never a billing number.
    Sorted so the rows with a co-worked project (the reassignment candidates) come first."""
    # Canonicalize casing first: heartbeats carry historical casing variants (own/CapacityManager
    # vs own/capacitymanager) which would otherwise split one project into two rows -- the same
    # normalisation collect() applies to the timesheet rows.
    hbs = []
    for hb in rollup.load_heartbeats():
        if not hb.get("session"):
            continue
        hb = dict(hb, project=canon.get(hb["project"].lower(), hb["project"]))
        hbs.append(hb)
    by_ds = {}
    for hb in hbs:
        by_ds.setdefault((hb["date"], hb["session"]), []).append(hb)

    # How much internal time each project STILL has on each finalized day. Heartbeats are
    # immutable (README: correct the timesheet, never the heartbeats), so without this the panel
    # keeps offering already-reassigned stretches forever and a second Apply would double-count.
    remaining = {}
    for date in {d for d, _ in by_ds}:
        sheet = rollup.parse_daily_file(date)
        if sheet is None:
            continue                      # not finalized yet -> nothing has been applied to it
        per = {}
        for r in sheet:
            if not r["billable"]:
                per[r["project"].lower()] = round(per.get(r["project"].lower(), 0.0)
                                                  + r["hours"], 2)
        remaining[date] = per

    mem, rows = memory_index(), []
    for (date, sess), group in by_ds.items():
        projects = {hb["project"] for hb in group}
        internal = sorted(p for p in projects if p == "Dev" or p.lower().startswith("own/"))
        if not internal:
            continue
        co = sorted(p for p in projects if p not in internal)
        turns = mem.get(sess, [])
        same = [t for d, t in turns if d == date.replace("-", "")]
        ev = list(dict.fromkeys(same or [t for _, t in turns]))[:3]   # dedupe, keep order
        for proj in internal:
            sub = [hb for hb in group if hb["project"] == proj]
            hours = round(sum(r["hours"] for r in rollup.rows_for(sub)), 2)
            if hours <= 0:
                continue
            # applied = the day is finalized and this project has NO internal hours left on it,
            # so every stretch it holds has already been reassigned. A partial move cannot be
            # attributed to one stretch, so anything above zero stays open for triage.
            left = remaining.get(date)
            applied = left is not None and left.get(proj.lower(), 0.0) <= 0
            rows.append({"date": date, "session": sess, "project": proj, "hours": hours,
                         "turns": len(sub), "co": co, "evidence": ev, "applied": applied,
                         "remaining": None if left is None else left.get(proj.lower(), 0.0),
                         "scope": "dev" if proj == "Dev" else "own"})
    rows.sort(key=lambda r: (r["applied"], not r["co"], r["date"], -r["hours"]))
    return rows


def last_heartbeat_by_session():
    """{session8: last ts_end (UTC datetime)} -- the only evidence a tagged session still exists."""
    seen = {}
    for hb in rollup.load_heartbeats():
        s = (hb.get("session") or "")[:8]
        if s and (s not in seen or hb["end"] > seen[s]):
            seen[s] = hb["end"]
    return seen


# ---------- F&O time entry ----------

# Excel 'Kunde' values that do not normalize onto the workspace customer folder. Everything else
# matches after lowercasing and folding spaces/hyphens/Danish letters (Vestforbraending, Element
# Logic, Carl-Ras all resolve on their own).
_norm_customer = fno.norm


def read_companies():
    """ops/TidsregInfo.xlsx -> [{firma, kunde, key, projektnr, aktivitet, task_note}].

    Lives in the read layer (`lib/fno.companies`) because the per-turn attribution check
    needs the same sheet to know whether a line will be enterable. Kept as a name here so
    the call sites -- and the tests that stub it -- do not care where it moved."""
    return fno.companies(ROOT)


def _fix_targets(row, rule, proj):
    """The files that can supply what this row is missing, most durable first.

    Two kinds. A SOURCE fix (the project's `fno_code`, the customer node's rule) stops the gap
    recurring on every future line; a ROW fix edits this one finalized day, which is what
    ops/time/README.md means by "edit this file to correct". Both are offered, because a code
    that only arrives next month still leaves this month's lines to type."""
    out = []
    kinds = set(m["field"] for m in row.get("missing") or ())
    if "proj_id" in kinds and proj.get("path"):
        out.append({"kind": "project", "field": "fno_code", "target": row["project"],
                    "label": "Set fno_code on " + row["project"]})
    if "description" in kinds and proj.get("path"):
        out.append({"kind": "project", "field": "fno_description", "target": row["project"],
                    "label": "Set fno_description on " + row["project"]})
    if kinds and rule:
        out.append({"kind": "customer", "field": "", "target": rule["customer"],
                    "label": "Rule: " + rule["customer"] + "/CLAUDE.md"})
    if kinds:
        out.append({"kind": "row", "field": "", "target": row["date"],
                    "label": "Correct this day's timesheet"})
    return out


def collect_entry(entries, customers, today, projects=None, tasks=None):
    """F&O entry rows: one per date/customer/project/activity/task, tagged with the internal
    company (Firma). F&O takes one timesheet PER COMPANY, so the company is the outermost grouping
    on the page -- it is the thing you open a separate sheet for.

    Every row also says whether it can actually be TYPED: `missing` lists the F&O fields the
    customer's own rule requires and the row cannot supply (ops/lib/fno.py, from the customer
    node). A row with a non-empty `missing` is the thing to fix before the month is entered, and
    `fix` says which file to fix it in.

    Returned FLAT (every date, not pre-bucketed) so the timesheet page can slice any range --
    an ISO week (the entry surface) or a calendar month (the overview) -- without the collector
    knowing which."""
    comp = read_companies()
    by_key = {c["key"]: c for c in comp}
    ws_keys = {_norm_customer(c): c for c in customers}
    cust_rules = fno.rules(ROOT)
    projects = projects or {}
    # One read per month that has time, not one per row. A day with no description file
    # simply has none -- the page falls back to the session evidence it already carries.
    descs = {}
    for month in sorted({e["date"][:7] for e in entries}):
        descs.update(linedesc.read_month(month))
    # The register wins over the timesheet's own Billable column, so a decision taken
    # after a day was written is honoured without rewriting it (ops/lib/noinvoice.py).
    marks = noinvoice.entries()

    def decorate(e, agg, unmapped):
        """One timesheet entry -> one F&O entry row (company, customer, resolved Proj ID)."""
        p = e["project"]
        cust = p.split("/")[1] if p.lower().startswith("customers/") and "/" in p else ""
        row_c = by_key.get(_norm_customer(cust)) if cust else None
        rule = cust_rules.get(_norm_customer(cust)) if cust else None
        if cust and row_c is None and rule is None:
            unmapped[cust] = round(unmapped.get(cust, 0.0) + e["hours"], 2)
        # The timesheet's own Billable column, honoured. A customer line set to `no` is
        # work for that client that is not going on an invoice -- registering time, fixing
        # the setup, the dashboard itself. It stays attributed to the client so the cost is
        # visible, and it is grouped with Internal here so it is never typed into F&O and
        # never counted as short of a dimension it does not need.
        no_entry = bool(cust) and (
            not e.get("billable", True)
            or bool(noinvoice.covers(e["date"], p, e["activity"], e["fno_task"], marks)))
        firma = ("INTERNAL" if no_entry else
                 ((rule or {}).get("firma") or (row_c["firma"] if row_c else "")
                  or ("" if cust else "INTERNAL")))

        # How the three dimensions resolve is one rule, in the read layer, because the
        # per-turn attribution check has to reach the same verdict about whether a line can
        # be typed. `fno_task: none` is the task-file convention for "no work item yet" and
        # is blanked here, so the line reads as short of one instead of carrying the word.
        ws_id = e["proj_id"]
        dims = fno.resolve_dims(ws_id, e["activity"], rule, row_c)
        proj_id, activity = dims["proj_id"], dims["activity"]
        conflict = dims["conflict"]
        xl_id = (rule or {}).get("proj_id") or (row_c["projektnr"] if row_c else "")
        fno_task = fno.value_or_blank(e["fno_task"])
        proj = projects.get(p) or {}
        description = proj.get("fno_description") or (rule or {}).get("description") or ""
        # What the work WAS, written at /log (ops/lib/lines.py). Keyed on the timesheet's
        # own dimensions, because that is the file it was written beside -- not on the
        # resolved ones, which may have been filled in from the sheet afterwards.
        summary = descs.get(e["date"], {}).get(
            linedesc.dimkey(p, e["activity"], e["fno_task"]), "")

        # `ws_*` is the line AS THE TIMESHEET FILE HOLDS IT, which is not what the row
        # shows: a blank fno_code reads as "" here after the sheet declines to fill it, and
        # an activity can come from the sheet rather than from the day. Correcting the file
        # matches on these, so they travel with the row. When two timesheet lines fold into
        # one cell and disagree, the cell is `ambiguous` and the editor will not write --
        # naming one of them would correct the wrong line.
        k = (firma, e["date"], cust, p, proj_id, activity, fno_task, no_entry)
        cell = agg.setdefault(k, {"firma": firma, "date": e["date"], "customer": cust,
                                  "project": p, "proj_id": proj_id, "activity": activity,
                                  "fno_task": fno_task, "hours": 0.0,
                                  "from_sheet": dims["from_sheet"], "conflict": conflict,
                                  "ws_proj_id": ws_id, "ws_activity": e["activity"],
                                  "ws_fno_task": e["fno_task"],
                                  "xl_proj_id": xl_id, "ambiguous": False,
                                  "description": description, "summary": summary,
                                  "no_charge": bool((rule or {}).get("no_charge")),
                                  "no_entry": no_entry,
                                  "requires": (rule or {}).get("requires") or [],
                                  # A day still accruing has no finalized file, so it cannot
                                  # be corrected -- the editor has to say that, not fail.
                                  "live": bool(e.get("live")),
                                  "task_note": row_c["task_note"] if row_c else ""})
        if (cell["ws_proj_id"] != ws_id or cell["ws_activity"] != e["activity"]
                or cell["ws_fno_task"] != e["fno_task"]):
            cell["ambiguous"] = True
        if summary and summary not in cell["summary"]:
            cell["summary"] = (cell["summary"] + " " + summary).strip()
        cell["hours"] = round(cell["hours"] + e["hours"], 2)
        # Nothing that is not being entered can be short of what entry requires.
        cell["missing"] = [] if no_entry else fno.missing(cell, rule)
        cell["fix"] = _fix_targets(cell, rule, proj)

    def build(src):
        a, u = {}, {}
        for e in src:
            decorate(e, a, u)
        return (sorted(a.values(), key=lambda r: (r["firma"], r["date"], r["customer"],
                                                  r["project"], r["activity"])), u)

    rows, unmapped = build(entries)

    # Consolidated variants. The scatter of sub-2 h day-entries is exactly what
    # rollup.consolidate_week exists for (ops/time/README.md sec.5, and what /time shows by
    # default) -- reuse it rather than reimplement the rule in the page. It groups by ISO week,
    # so each range the page can show gets its own pass; totals are unchanged, only the spread
    # across days.
    d0 = datetime.date.fromisoformat(today)
    ranges = {}
    for key, first in (
            ("month0", d0.replace(day=1)),
            ("month1", (d0.replace(day=1) - datetime.timedelta(days=1)).replace(day=1))):
        nxt = (first.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
        span = (nxt - first).days
        ranges[key] = [(first + datetime.timedelta(days=i)).isoformat() for i in range(span)]

    # The week page is the entry surface, and its picker walks the same AUDIT_WEEKS the audit
    # sections do -- so every one of those weeks needs its own range and its own consolidation
    # pass, keyed by the ISO week itself.
    #
    # A week that straddles a month boundary (W31 is 27 Jul - 2 Aug) additionally gets one range
    # PER MONTH, keyed '<week>@<YYYY-MM>'. F&O takes a timesheet per month, and consolidation packs
    # a week's hours onto as few days as it can -- over a whole straddling week that would move
    # hours across the boundary and misstate both months. Consolidating each segment on its own is
    # what keeps the month totals true.
    for m in audit_mondays(today):
        iso = m.isocalendar()
        wk = "%04d-W%02d" % (iso[0], iso[1])
        days = [(m + datetime.timedelta(days=i)).isoformat() for i in range(7)]
        ranges[wk] = days
        by_month = {}
        for d in days:
            by_month.setdefault(d[:7], []).append(d)
        if len(by_month) > 1:
            for mk, ds in by_month.items():
                ranges["%s@%s" % (wk, mk)] = ds

    merged = {}
    for key, dates in ranges.items():
        inr = set(dates)
        src = [e for e in entries if e["date"] in inr]
        if not src:
            merged[key] = []
            continue
        merged[key] = build(rollup.consolidate_week(src, dates, ENTRY_MERGE_THRESHOLD))[0]

    # The readiness gate for the whole payload, so a page can say "3 lines cannot be typed"
    # without walking every range itself. Counted on the RAW rows: consolidation moves hours
    # between days, it never fills in a missing dimension.
    short = [r for r in rows if r["missing"]]

    # What each F&O task id is called. The id is all that goes on a line; the name is so
    # the right one can be picked out of ten at entry time (ops/lib/fnotasks.py).
    used = sorted({r["fno_task"] for r in rows if r["fno_task"]}
                  | {(t.get("fno_task") or "").strip() for t in (tasks or [])
                     if (t.get("fno_task") or "").strip() not in ("", "none", "-")})
    task_names = fnotasks.resolve(used, tasks or [])

    return {
        "rows": rows,
        "task_names": task_names,
        "merged": merged,
        "ranges": ranges,
        "short": short,
        "rules": {k: v for k, v in cust_rules.items()},
        "companies": sorted({c["firma"] for c in comp}),
        "mapping": comp,
        "unmapped": sorted(({"customer": k, "hours": v} for k, v in unmapped.items()),
                           key=lambda x: -x["hours"]),
        "no_project": sorted(c["kunde"] for c in comp if c["key"] not in ws_keys),
        "reclaim": reclaim_placed(),
    }


def reclaim_placed():
    """Reclaimed hours placed on a later day (ops/time/reclaim.md, consumption log) ->
    [{date, project, hours}]. Registered on that date, not worked on it, so a check of
    what was billed against what was measured has to hold them apart."""
    out = []
    try:
        with open(os.path.join(ROOT, "ops", "time", "reclaim.md"), encoding="utf-8") as f:
            text = f.read()
    except Exception:
        return out
    for line in text.split("Consumption log:", 1)[-1].splitlines():
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) >= 3 and re.match(r"^\d{4}-\d{2}-\d{2}$", c[0]):
            try:
                out.append({"date": c[0], "project": c[1], "hours": float(c[2])})
            except ValueError:
                pass
    return out


def _turns_today(today):
    """{session8: {project: turns}} from today's heartbeats."""
    out = {}
    for hb in rollup.load_heartbeats():
        if hb["date"] != today:
            continue
        sid = (hb.get("session") or "")[:8]
        if not sid:
            continue
        p = hb.get("project") or "Dev"
        out.setdefault(sid, {})
        out[sid][p] = out[sid].get(p, 0) + 1
    return out


def active_sessions(today=None):
    """Every session that produced time today, what it holds, and whether the two agree.

    Three questions in one row, because they are one question: what task did this session
    start with, what projects are its turns actually landing on, and will those turns
    produce a line that can be entered. The last is `lib/attribution.drift`, the same
    judgement the per-turn hook makes, so the page and the nudge cannot disagree.

    Task tags recorded in ops/time/active-task, each marked live or stale.

    The file records which tag a SESSION ID holds and keeps entries for 7 days (ops/time/README.md
    sec.2) -- it says nothing about whether that session still exists. A closed window therefore
    leaves a tag behind that used to be reported as 'time is billing to that task' when nothing was
    being written. Liveness comes from the heartbeats instead, using the rollup's own IDLE_TIMEOUT
    so 'live' means the same thing here as it does in the 15+5 model."""
    raw = read(os.path.join(ROOT, "ops", "time", "active-task")).strip()
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except Exception:
        return [{"slug": raw.splitlines()[0].strip(), "session": "", "set_at": ""}]
    out = []
    if isinstance(data, dict) and "sessions" in data:
        for sid, rec in (data.get("sessions") or {}).items():
            out.append({"slug": rec.get("slug", ""), "session": sid[:8],
                        "set_at": rec.get("set_at", "")})
        unc = data.get("unclaimed")
        if unc:
            out.append({"slug": unc.get("slug", ""), "session": "unclaimed",
                        "set_at": unc.get("set_at", "")})
    elif isinstance(data, dict):
        out.append({"slug": data.get("slug", ""), "session": (data.get("session") or "")[:8],
                    "set_at": data.get("set_at", "")})

    # Every session that produced time today, whether or not it holds a task. The old
    # list was the held tasks alone -- which is the set of sessions with nothing wrong
    # with them, so the page could not show the problem it exists to show.
    held = {o["session"] for o in out}
    for sid in sorted(_turns_today(today)):
        if sid not in held:
            out.append({"slug": "", "session": sid, "set_at": ""})

    seen = last_heartbeat_by_session()
    now = datetime.datetime.now(datetime.timezone.utc)
    # Three states, because last-heartbeat is the ONLY evidence and it cannot prove a window is
    # open. 'live' reuses the rollup's IDLE_TIMEOUT (a stretch is still accruing); 'idle' is a
    # window that may well be open but is not being worked; 'stale' outlived its session and is
    # what makes the alert lie. No heartbeat at all -> stale (tag set, session never tracked).
    live_min = rollup.IDLE_TIMEOUT.total_seconds() / 60
    STALE_MIN = 12 * 60
    for o in out:
        hb = seen.get(o["session"])
        mins = (now - hb).total_seconds() / 60 if hb else None
        o["last_seen"] = hb.strftime("%Y-%m-%d %H:%M") if hb else ""
        o["idle_min"] = round(mins) if mins is not None else None
        o["state"] = ("stale" if mins is None or mins > STALE_MIN
                      else "live" if mins <= live_min else "idle")

    # What each one is actually producing, and whether it can be entered.
    turns = _turns_today(today or datetime.date.today().isoformat())
    rules, sheet = fno.rules(ROOT), fno.companies(ROOT)
    for o in out:
        landed = turns.get(o["session"]) or {}
        o["landed"] = [{"project": p, "turns": n}
                       for p, n in sorted(landed.items(), key=lambda kv: -kv[1])]
        o["turns"] = sum(landed.values())
        o["held_project"] = _task_project(o["slug"]) if o["slug"] else ""
        found = []
        for p in landed:
            d = attribution.drift(p, o["slug"] if p == o["held_project"] else "",
                                  o["slug"], o["held_project"], rules, sheet, ROOT)
            if d:
                found.append(d)
        o["drift"] = found
    # A stale tag with no turns today is last week's leftover, not a session.
    return [o for o in out if o["slug"] or o["turns"]]


def _task_project(slug):
    """The project a task slug belongs to, or "" -- the task file's own `project:`."""
    if not slug:
        return ""
    for state in ("in-progress", "open", "done", "cancelled"):
        p = os.path.join(ROOT, "ops", "tasks", state, slug + ".md")
        if os.path.exists(p):
            fm, _ = frontmatter(read(p))
            return fm.get("project", "") or ""
    return ""


def collect_todos():
    """The unchecked captures in ops/TODO.md.

    `line` and `raw` carry the source position, so ticking one can rewrite exactly that
    line and refuse if the file moved underneath the page."""
    text = read(os.path.join(ROOT, "ops", "TODO.md"))
    open_items = []
    for i, line in enumerate(text.splitlines()):
        m = re.match(r"^- \[ \]\s*(\d{4}-\d{2}-\d{2})?\s*[-\u2014]?\s*(.*)$", line.strip())
        if m:
            open_items.append({"date": m.group(1) or "", "text": plain(m.group(2))[:300],
                               "line": i, "raw": line})
    return open_items


# ---------- project status (the Projects table) ----------

DORMANT_RE = re.compile(r"complete|delivered|archived", re.I)
INFLIGHT_DAYS = 14


def project_band(p):
    """Which band a project sits in on the Projects page.

    The same rule the overview applied in the browser, moved here so one definition
    serves every page and can be tested:
      workspace  the Dev bucket, which is not a project
      dormant    the context says complete / delivered / archived
      inflight   worked within INFLIGHT_DAYS
      quiet      active, but nobody has touched it"""
    if p["key"] == "Dev":
        return "workspace"
    if DORMANT_RE.search(p.get("ctx_status", "") or ""):
        return "dormant"
    idle = p.get("days_idle")
    return "inflight" if idle is not None and idle <= INFLIGHT_DAYS else "quiet"


EMPTY_COUNTS = {"in_progress": 0, "open": 0, "parked": 0, "due_back": 0,
                "stalled": 0, "asks_unsent": 0, "devops": 0, "total": 0}


def merge_card_fields(projects):
    """Add the resume-card and task-count fields the Projects table needs.

    They already exist in the day-brief model, which parses the same cards; borrowing
    them keeps one parser rather than two that can disagree. The card's `blocked_on` is
    a list of PEOPLE and its `open_threads` is a COUNT, so neither can reuse the name
    the CONTEXT State block already holds on the project."""
    model = _daybrief_model()
    by_key = {b["key"]: b for b in model.get("projects", [])}
    for key, p in projects.items():
        b = by_key.get(key) or {}
        card = b.get("card") or {}
        p["card_shape"] = card.get("shape", "none")
        p["goal"] = card.get("goal", "")
        p["standing_date"] = card.get("standing_date", "")
        p["blocked_people"] = card.get("blocked_on", []) or []
        p["card_threads"] = card.get("open_threads", 0) or 0
        p["counts"] = b.get("counts") or dict(EMPTY_COUNTS)


# ---------- assembly ----------

CACHE_TTL = 30.0                       # s
_cache = {"data": {"at": 0.0, "v": None}, "today": {"at": 0.0, "v": None}}
_cache_lock = threading.Lock()


def _memo(name, build, force=False):
    """Serve `name` from the memo, or rebuild it.

    One walk reads every task file, every CLAUDE.md and CONTEXT.md, every heartbeat and
    the XLSX. Without this, Refresh, the 60 s auto-refresh and three pages sharing one
    payload each pay for a full walk. The lock is held across the build so two concurrent
    misses do not both walk; every write path calls invalidate(), so a change you just
    made is never hidden behind the memo."""
    slot = _cache[name]
    with _cache_lock:
        if not force and slot["v"] is not None and time.monotonic() - slot["at"] < CACHE_TTL:
            return slot["v"]
        slot["v"] = build()
        slot["at"] = time.monotonic()
        return slot["v"]


def collect(force=False):
    """The dashboard payload -- projects, customers, tasks, time, hygiene."""
    return _memo("data", _collect, force)


def collect_daybrief(force=False):
    """The day-brief model -- the task view Today renders, with its progress dates."""
    return _memo("today", _daybrief_model, force)


def invalidate():
    """Drop both memos, so the next read sees what a write just did."""
    with _cache_lock:
        for slot in _cache.values():
            slot["v"] = None


def _collect():
    today = rollup.to_local(datetime.datetime.now(datetime.timezone.utc)).strftime("%Y-%m-%d")
    projects, customers = discover()
    tasks = collect_tasks()
    entries, unfinalized = collect_time(today)
    todos = collect_todos()
    for t in todos:
        t["age"] = days_ago(t["date"], today) if t["date"] else None

    # canonical key match (timesheets carry historical casing and merged/deleted folders)
    lookup = {k.lower(): k for k in projects}
    for c in customers:
        lookup[("customers/" + c).lower()] = "node:customers/" + c

    hours, by_date_proj, orphans, unset = {}, {}, {}, {}
    daily = {}
    for e in entries:
        key = lookup.get(e["project"].lower())
        if key is None:
            orphans[e["project"]] = orphans.get(e["project"], 0.0) + e["hours"]
            key = "orphan:" + e["project"]
        h = hours.setdefault(key, {"total": 0.0, "d30": 0.0, "month": 0.0, "last": ""})
        h["total"] += e["hours"]
        if e["date"][:7] == today[:7]:
            h["month"] += e["hours"]
        age = days_ago(e["date"], today)
        if age is not None and age <= 30:
            h["d30"] += e["hours"]
        if e["date"] > h["last"]:
            h["last"] = e["date"]
        by_date_proj.setdefault(key, {}).setdefault(e["date"], 0.0)
        by_date_proj[key][e["date"]] += e["hours"]
        low = e["project"].lower()
        scope = ("customers" if low.startswith("customers/")
                 else "own" if low.startswith("own/") else "dev")
        d = daily.setdefault(e["date"], {"customers": 0.0, "own": 0.0, "dev": 0.0})
        d[scope] += e["hours"]
        if e["proj_id"] in ("UNSET", "") or e["proj_id"].startswith("PENDING"):
            unset[e["project"]] = unset.get(e["project"], 0.0) + e["hours"]

    tasks_by_project = {}
    for t in tasks:
        tasks_by_project.setdefault(t["project"], []).append(t)

    for key, p in projects.items():
        h = hours.get(key, {"total": 0.0, "d30": 0.0, "month": 0.0, "last": ""})
        p["hours"] = round(h["total"], 2)
        p["hours_30d"] = round(h["d30"], 2)
        p["hours_month"] = round(h["month"], 2)
        p["by_date"] = by_date_proj.get(key, {})
        last = max([x for x in (h["last"], p.get("last_worked", "")) if x] or [""])
        p["last_activity"] = last
        p["days_idle"] = days_ago(last, today) if last else None
        p["tasks"] = [t["slug"] for t in tasks_by_project.get(key, [])
                      if t["state"] in ("open", "in-progress")]
        p["tasks_done"] = len([t for t in tasks_by_project.get(key, []) if t["state"] == "done"])
        p["band"] = project_band(p)

    merge_card_fields(projects)

    for cname, c in customers.items():
        nk = "node:customers/" + cname
        c["node_hours"] = round(hours.get(nk, {}).get("total", 0.0), 2)
        c["hours"] = round(c["node_hours"] + sum(projects[k]["hours"] for k in c["projects"]), 2)
        c["hours_30d"] = round(sum(projects[k]["hours_30d"] for k in c["projects"]), 2)
        lasts = [projects[k]["last_activity"] for k in c["projects"] if projects[k]["last_activity"]]
        nl = hours.get(nk, {}).get("last", "")
        if nl:
            lasts.append(nl)
        c["last_activity"] = max(lasts) if lasts else ""
        c["days_idle"] = days_ago(c["last_activity"], today) if c["last_activity"] else None
        c["open_tasks"] = sum(len(projects[k]["tasks"]) for k in c["projects"])

    week = rollup.week_key(today)
    tot = {"today": 0.0,
           "week_billable": 0.0, "week_internal": 0.0,
           "month_billable": 0.0, "month_internal": 0.0,
           "all_billable": 0.0, "all_internal": 0.0}
    for date, v in daily.items():
        bill, intern_ = v["customers"], v["own"] + v["dev"]
        tot["all_billable"] += bill
        tot["all_internal"] += intern_
        if date[:7] == today[:7]:
            tot["month_billable"] += bill
            tot["month_internal"] += intern_
        if rollup.week_key(date) == week:
            tot["week_billable"] += bill
            tot["week_internal"] += intern_
    tot["today"] = round(sum(daily.get(today, {}).values()), 2)
    tot = {k: round(v, 2) for k, v in tot.items()}

    # Per-scope, so the chart can follow the Customers/Own/Dev filter. The window starts at the
    # first of LAST month -- the chart offers this-month / last-month and fills absent dates with 0.
    first_this = datetime.date.fromisoformat(today).replace(day=1)
    cutoff = (first_this - datetime.timedelta(days=1)).replace(day=1).isoformat()
    daily_series = [{"date": d, "customers": round(v["customers"], 2),
                     "own": round(v["own"], 2), "dev": round(v["dev"], 2)}
                    for d, v in sorted(daily.items()) if d >= cutoff]

    return {
        "generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "today": today, "week": week, "root": ROOT,
        "totals": tot, "daily": daily_series,
        "projects": [projects[k] for k in sorted(projects)],
        "customers": [customers[k] for k in sorted(customers)],
        "tasks": tasks,
        # canonical display key per lowercased path (customer nodes keep their plain path here --
        # the "node:" prefix is an internal grouping key, not something to show or bill to)
        "internal": collect_internal(
            dict({k.lower(): k for k in projects},
                 **{("customers/" + c).lower(): "customers/" + c for c in customers})),
        # F&O is Project ID -> Activity -> Task (ops/time/README.md sec.4), so a reassignment
        # target is a project AND optionally one of its tasks, which carries the two sub-dimensions.
        "targets": [{"project": t["project"], "slug": t["slug"], "title": t["title"],
                     "state": t["state"], "activity": t["activity"], "fno_task": t["fno_task"]}
                    for t in tasks if t["state"] in ("open", "in-progress") and t["project"]],
        "entry": collect_entry(entries, customers, today, projects, tasks),
        "audit": collect_audit(today),
        "lineSessions": collect_line_sessions(today),
        "active_sessions": active_sessions(today),
        "todos": todos,
        "hygiene": {
            "unfinalized": unfinalized,
            "unset": sorted(({"project": k, "hours": round(v, 2)} for k, v in unset.items()),
                            key=lambda x: -x["hours"]),
            "unset_total": round(sum(unset.values()), 2),
            "orphans": sorted(({"project": k, "hours": round(v, 2)} for k, v in orphans.items()),
                              key=lambda x: -x["hours"]),
            "todo_open": len(todos),
        },
        "thresholds": {"good": FRESH_GOOD, "warn": FRESH_WARN, "serious": FRESH_SERIOUS},
    }


# ---------- launch ----------

def launch(path, mode, prompt=""):
    """Act on `path`: open a session ('claude'), a folder ('code'), or a file ('file').
    'claude' may carry an initial `prompt` (e.g. a /task invocation). Returns (ok, message)."""
    if mode not in ("claude", "code", "file"):
        return False, "unknown launch mode: %r" % mode
    # An empty path is not the workspace root: abspath("") is the server's own working
    # directory, which is inside ROOT and exists, so it would pass the guard below and
    # start a session wherever the server happens to be running.
    if not path:
        return False, "no path given"
    path = os.path.abspath(path)
    if not path.lower().startswith(ROOT.lower()) or not os.path.exists(path):
        return False, "path outside the workspace"

    if mode in ("code", "file"):
        exe = shutil.which("code")
        if not exe:
            return False, "VS Code CLI ('code') not on PATH"
        args = [exe, "-r", "-g", path] if mode == "file" else [exe, path]
        # CreateProcess cannot run a .cmd/.bat directly -- go through cmd.exe
        cmd = ["cmd", "/c"] + args if exe.lower().endswith((".cmd", ".bat")) else args
        subprocess.Popen(cmd, cwd=ROOT, shell=False)
        return True, ("Opened in VS Code: " if mode == "file" else "VS Code opened at ") + path

    cwd = path if os.path.isdir(path) else os.path.dirname(path)
    wt = shutil.which("wt")
    claude = shutil.which("claude")
    if not claude:
        return False, "'claude' not on PATH"
    argv = [claude] + ([prompt] if prompt else [])
    if wt:
        subprocess.Popen([wt, "-d", cwd] + argv, cwd=cwd, shell=False)
    else:
        subprocess.Popen(["cmd", "/c", "start", "", "cmd", "/k"] + argv, cwd=cwd, shell=False)
    return True, ("Session starting at %s%s" % (cwd, " with: " + prompt[:60] if prompt else ""))


# ---------- reassign (the one write path) ----------
# Dev -> project only. ops/time/README.md sec.2 and memory feedback-time-attribution-dev-to-project:
# time already on a NAMED project stays there, and is never moved between two named projects by
# judgement. The UI only offers the control on Dev rows; this refuses anything else regardless,
# because a rule enforced only in the page is not enforced.
#
# Both halves of a line move together. The audit joins the CLAIM (timesheet/<date>.md) to its
# EVIDENCE (value/<date>.jsonl) on (date, project, activity, task) -- move one and the row lands
# under the new project with nothing behind it, and an orphan sits under the old one.


def never_invoice(date, row, to_project="", note=""):
    """Say a line is never invoiced, and optionally where it belongs instead.

    Three things happen, in this order, because the first must hold even if the others
    cannot:

    1. the decision goes on the register (`ops/time/not-invoiced.md`), which wins over the
       folder, the timesheet file and any later correction -- so it holds on a day that is
       still running, before a day file exists at all
    2. if the day is finalized, the line is moved and/or its `Billable` column set to `no`,
       so the file agrees with the register rather than contradicting it
    3. if it is not finalized yet, nothing is written to a timesheet -- the rollup applies
       the register when it writes the day

    That ordering is the whole point of "under any circumstances": the mark is recorded
    first and survives everything downstream of it."""
    project = (row or {}).get("project") or ""
    if not project.startswith("customers/"):
        return False, "%s is not invoiced anyway" % (project or "that line")
    ok, msg = noinvoice.record(date, project, (row or {}).get("activity") or "",
                               (row or {}).get("fno_task") or "", note)
    if not ok:
        return False, msg
    invalidate()

    if rollup.parse_daily_file(date) is None:
        return True, ("%s. %s is still running, so there is no timesheet to change -- the "
                      "rollup will write it not billable when the day closes."
                      % (msg, date))
    moved, mmsg = reassign(date, row, to_project, billable=False, note=note)
    return True, ("%s. %s" % (msg, mmsg) if moved
                  else "%s, but the timesheet line could not be changed: %s" % (msg, mmsg))


def _reassign_note(date, src_project, to_project, hours, billable, note):
    """The line the correction leaves in the day file. It has to say what moved, where,
    and whether it is going on an invoice -- a reader six weeks later has only this."""
    what = ("%s -> %s" % (src_project, to_project) if to_project != src_project
            else "%s, in place" % src_project)
    bill = "billable" if billable else "NOT for registration"
    why = (" -- " + re.sub(r"\s+", " ", note).strip()[:300]) if note else ""
    return ("\n> Reassigned %s: %s (%.2f h), %s, from the dashboard.%s\n"
            "> Heartbeats untouched; the value records moved with it.\n"
            % (date, what, hours, bill, why))


def _is_place(key):
    """Somewhere time can be attributed: a project, a customer node, or the workspace.

    A customer NODE is a legitimate destination even though it is not a project -- it is
    where work for a client that is not on any one project belongs (ADR-003, 2026-07-28).
    It has no `fno_code`, so it never produces an enterable line, which is exactly right
    for work that is not going to be invoiced."""
    if key == "Dev":
        return True
    if re.match(r"^customers/[^/]+$", key):
        return os.path.isdir(os.path.join(ROOT, key.replace("/", os.sep)))
    if re.match(r"^(customers/[^/]+/[^/]+|own/[^/]+)$", key):
        return os.path.exists(os.path.join(ROOT, key.replace("/", os.sep), "CLAUDE.md"))
    return False


def reassign(date, row, to_project="", billable=None, note=""):
    """Move one timesheet line somewhere else, and/or say it is not to be registered.

    Two things a line can need, often together:

      MOVE      work booked to a customer project that was really workspace work -- time
                registration itself, fixing the setup, this dashboard -- belongs on `Dev`,
                on an `own/` project, or on the customer NODE when it is for that client
                but not on any one project.
      UNBILLABLE  a line that stays where it is but is not going on an invoice. The
                timesheet already has a `Billable` column; setting it to `no` is what the
                entry page reads to leave the line out of the F&O blocks while still
                counting the hours against that client.

    The direction matters. Moving a customer line to Dev/own, or marking one unbillable,
    REDUCES what is invoiced and is always allowed. Moving Dev or own time ONTO a customer
    is the direction that over-bills (ops/time/README.md sec.2), so it stays what it has
    always been: a deliberate call at the review gate, one line at a time, which is what
    this is. What is refused is moving one customer's time to another customer -- that is
    two invoices wrong, and no single click should be able to do it.

    -> (ok, message)."""
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date or ""):
        return False, "bad date"
    to_project = (to_project or "").strip().replace("\\", "/").strip("/")
    if to_project and not _is_place(to_project):
        return False, "%s is not a project, a customer or the workspace" % to_project
    if not to_project and billable is None:
        return False, "nothing to do: name a destination or set billable"

    rows = rollup.parse_daily_file(date)
    if rows is None:
        return False, "no finalized timesheet for %s -- close the day first" % date

    want = (row.get("project") or "", (row.get("proj_id") or "").strip(),
            (row.get("activity") or "").strip(), (row.get("fno_task") or "").strip())
    src = [r for r in rows
           if (r["project"], (r["proj_id"] or "").strip(), (r["activity"] or "").strip(),
               (r["fno_task"] or "").strip()) == want]
    if len(src) != 1:
        return False, ("that line is no longer on %s -- refresh" % date if not src
                       else "%d lines match -- correct %s by hand" % (len(src), date))
    src_project = src[0]["project"]
    from_cust = customer_name(src_project)
    to_cust = customer_name(to_project) if to_project else from_cust
    if from_cust and to_cust and from_cust != to_cust:
        return False, ("%s to %s moves one customer's time to another -- do that by hand, "
                       "with a reason" % (from_cust, to_cust))

    activity = (src[0]["activity"] or "")
    fno_task = (src[0]["fno_task"] or "")
    to_project = to_project or src_project
    # An F&O activity and a DevOps work item belong to a customer. Carrying them onto Dev
    # or own/ would leave internal time wearing a customer's dimensions, and would stop
    # the moved hours merging into the internal line already there.
    if not to_project.lower().startswith("customers/"):
        activity = fno_task = ""
    moved = src[0]["hours"]
    proj_id = rollup.project_id(to_project)
    billable = (to_project.lower().startswith("customers/") if billable is None
                else bool(billable))
    keep = [r for r in rows if r is not src[0]]
    for r in keep:                                  # merge into an existing identical line
        if (r["project"] == to_project and r["activity"] == activity
                and r["fno_task"] == fno_task and r["billable"] == billable):
            r["hours"] = round(r["hours"] + moved, 2)
            break
    else:
        keep.append({"project": to_project, "proj_id": proj_id, "activity": activity,
                     "fno_task": fno_task, "hours": moved, "billable": billable})
    keep.sort(key=lambda r: (not r["billable"], r["project"], r["activity"], r["fno_task"]))

    # Everything after the totals block is prior provenance -- keep it, then add this move.
    raw = read(rollup.daily_path(date))
    tail = ""
    m = re.search(r"\*\*Internal total:\*\*[^\n]*\n", raw)
    if m:
        tail = raw[m.end():]
    rollup.write_daily(date, keep,
                       tail + _reassign_note(date, src_project, to_project, moved,
                                             billable, note))

    # the evidence side
    vpath = os.path.join(VALUE, date + ".jsonl")
    touched = 0
    if os.path.exists(vpath):
        out = []
        with open(vpath, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                v = json.loads(line)
                if (v.get("project") == src_project
                        and (v.get("activity") or "") == activity
                        and (v.get("fno_task") or "") == fno_task):
                    v["project"] = to_project
                    v["proj_id"] = proj_id
                    v["billable"] = billable
                    touched += 1
                out.append(json.dumps(v, sort_keys=True))
        with open(vpath, "w", encoding="utf-8") as f:
            f.write("\n".join(out) + "\n")
    what = ("marked %.2f h on %s not for registration" % (moved, src_project)
            if to_project == src_project
            else "moved %.2f h from %s to %s" % (moved, src_project, to_project))
    return True, "%s on %s (%d evidence record%s)" % (
        what, date, touched, "" if touched == 1 else "s")


# ---------- task mutations (direct-write: mechanical state only) ----------
# Session-free path for the day view: moving a task between states and updating
# frontmatter fields that carry no judgment. Writing a Progress block or a Next
# step still belongs to a session.
#
# Safety: the task must exist under ROOT/ops/tasks; only the listed actions are
# accepted -- no free-form writes.

def _read_raw(path):
    """-> (text with \n endings, was_crlf).

    A file that is read to be edited has to be written back the way it was found. The
    substrate is not uniform -- task files and CLAUDE.md are LF, the timesheet days and
    TODO.md are CRLF, because rollup.py writes those in text mode on Windows -- and
    flipping either turns a one-line correction into a whole-file diff."""
    with io.open(path, encoding="utf-8", newline="") as f:
        raw = f.read()
    return raw.replace("\r\n", "\n"), "\r\n" in raw


def _write_raw(path, text, crlf):
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text.replace("\n", "\r\n") if crlf else text)


FNO_FIELDS = ("fno_code", "fno_activity", "fno_description", "fno_firma",
              "fno_requires", "fno_billable")
# A dimension value is an F&O code, an activity id or a short description -- never prose and
# never a newline, which would break the `key: value` line it is written onto.
FNO_VALUE_RE = re.compile(r"^[\w\-.,:/() ]{0,120}$")


def _fm_line(key, val):
    return "%s: %s" % (key, val) if val else "%s:" % key


def _apply_fm(text, updates):
    """Apply {field: new_value} to the frontmatter block of a task file.
    Empty-string value writes 'field:' (blank). A field not already present is
    appended. Every other line is kept verbatim -- inline comments, key order,
    indented block values, and the blank line before the body.

    Values are written literally. The line is REPLACED, not regex-substituted:
    a value carrying a backslash (a Windows path) or a group reference is
    ordinary free text from the day view, and as a substitution template it
    would raise or silently rewrite itself."""
    m = re.match(r"^(---[ \t]*\n)(.*?\n)(---[ \t]*\n)", text, re.S)
    if not m:
        return text
    lines = m.group(2).splitlines()
    rest = text[m.end():]
    seen = set()
    for i, line in enumerate(lines):
        k = re.match(r"([A-Za-z_][\w-]*):", line)
        if k and k.group(1) in updates and k.group(1) not in seen:
            seen.add(k.group(1))
            lines[i] = _fm_line(k.group(1), updates[k.group(1)])
    for key, val in updates.items():
        if key not in seen:
            lines.append(_fm_line(key, val))
    return m.group(1) + "\n".join(lines) + "\n" + m.group(3) + rest


def _append_log(text, date_str, note):
    """Prepend a dated bullet to ## Log, creating the section if absent."""
    note = re.sub(r"\s+", " ", note).strip()[:500]
    entry = "- %s — %s\n" % (date_str, note)
    m = re.search(r"^(## Log[^\n]*\n)", text, re.M)
    if m:
        return text[:m.end()] + entry + text[m.end():]
    return text.rstrip("\n") + "\n\n## Log\n" + entry


def todo_mutate(index, action, raw):
    """Tick or drop one unchecked line of ops/TODO.md.

    The file is hand-maintained prose, so the write is surgical. The caller names the
    line number AND the line it was showing; if the two no longer agree the file moved
    under the page and nothing is written. Only that line's text changes -- its
    indentation, its inner spacing and its line ending are put back as they were, which
    is also what keeps a CRLF file from being rewritten wholesale."""
    if action not in ("tick", "drop"):
        return False, "unknown action: %r" % (action,)
    path = os.path.join(ROOT, "ops", "TODO.md")
    try:
        with io.open(path, encoding="utf-8", newline="") as f:
            text = f.read()
    except Exception as exc:
        return False, str(exc)
    lines = text.splitlines(keepends=True)
    if not isinstance(index, int) or isinstance(index, bool) or not 0 <= index < len(lines):
        return False, "line %r is outside TODO.md" % (index,)
    content = lines[index].rstrip("\r\n")
    ending = lines[index][len(content):]
    if content != raw:
        return False, "TODO.md changed since the page loaded -- refresh"
    m = re.match(r"^(\s*)- \[ \](\s*)(.*)$", content)
    if not m:
        return False, "not an unchecked item"
    indent, gap, body = m.group(1), m.group(2), m.group(3)
    today = datetime.date.today().isoformat()
    if action == "tick":
        new = "%s- [x]%s%s  (done %s)" % (indent, gap, body, today)
    else:
        new = "%s- [x]%s~~%s~~  (dropped %s)" % (indent, gap, body, today)
    lines[index] = new + ending
    try:
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write("".join(lines))
    except Exception as exc:
        return False, str(exc)
    return True, "%s: %s" % ("ticked" if action == "tick" else "dropped", body[:60])


def task_mutate(slug, action, **kwargs):
    """Mechanical task mutations from the day-view without a session.

    action: done | open | in-progress | ask-sent | ask-answered | ask-dropped | resume
            | park | wait | comment | set-dims
    kwargs: date (park), waiting_on (wait), text (comment, ask-dropped reason),
            activity + fno_task (set-dims)
    Returns (ok, message)."""
    if not re.match(r"^[\w-]+$", slug or ""):
        return False, "bad slug"
    found_state = found_path = None
    for state in ("in-progress", "open"):
        p = os.path.join(ROOT, "ops", "tasks", state, slug + ".md")
        if os.path.exists(p):
            found_state, found_path = state, p
            break
    if not found_path:
        return False, "task not found: %s" % slug

    text, crlf = _read_raw(found_path)
    updates = {}
    new_state = None

    if action == "done":
        new_state = "done"
        updates["status"] = "done"
    elif action == "open":
        if found_state != "in-progress":
            return False, "task is not in-progress"
        new_state = "open"
        updates["status"] = "open"
    elif action == "in-progress":
        if found_state != "open":
            return False, "task is not open"
        new_state = "in-progress"
        updates["status"] = "in-progress"
    elif action == "ask-sent":
        updates["customer_ask"] = "sent " + datetime.date.today().isoformat()
    elif action == "ask-answered":
        updates["customer_ask"] = "answered"
    elif action == "ask-dropped":
        # An ask that is no longer relevant, or was wrong. The flag clears so the day view
        # stops carrying it; the Log line keeps the fact that it was dropped, because the
        # bullet under `## Needs from customer` stays and would otherwise read as live.
        reason = (kwargs.get("text") or "no longer relevant").strip()
        text = _append_log(text, datetime.date.today().isoformat(),
                           "Customer ask dropped: %s" % reason)
        updates["customer_ask"] = "dropped"
    elif action == "resume":
        updates["waiting_on"] = ""
        updates["resume_on"] = ""
    elif action == "park":
        date = (kwargs.get("date") or "").strip()
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
            return False, "bad date: %r" % date
        updates["resume_on"] = date
        updates["waiting_on"] = ""
    elif action == "wait":
        wo = (kwargs.get("waiting_on") or "").strip()
        if not wo:
            return False, "waiting_on required"
        updates["waiting_on"] = wo
        updates["resume_on"] = ""
    elif action == "set-dims":
        # The F&O sub-dimensions this task lends to every line tagged with it
        # (ops/time/rollup.py task_dims). In F&O a Task carries its own Activity, so a
        # task-registering customer wants only the task; a customer with activities and no
        # tasks wants only the activity. Either may be set alone, and only what is sent is
        # written -- a field left out keeps whatever the file says.
        wrote = []
        for key in ("activity", "fno_task"):
            if key not in kwargs or kwargs[key] is None:
                continue
            val = str(kwargs[key]).strip()
            if not FNO_VALUE_RE.match(val):
                return False, "%s has characters that cannot go on a field line" % key
            updates[key] = val
            wrote.append("%s=%s" % (key, val or "(blank)"))
        if not wrote:
            return False, "nothing to set"
        try:
            _write_raw(found_path, _apply_fm(text, updates), crlf)
        except Exception as exc:
            return False, str(exc)
        return True, "%s: %s" % (slug, ", ".join(wrote))
    elif action == "comment":
        txt = (kwargs.get("text") or "").strip()
        if not txt:
            return False, "empty note"
        new_text = _append_log(text, datetime.date.today().isoformat(), txt)
        try:
            _write_raw(found_path, new_text, crlf)
        except Exception as exc:
            return False, str(exc)
        return True, "note added: %s" % slug
    else:
        return False, "unknown action: %r" % action

    new_text = _apply_fm(text, updates)
    target = (os.path.join(ROOT, "ops", "tasks", new_state, slug + ".md")
              if new_state else found_path)
    try:
        _write_raw(target, new_text, crlf)
        if new_state and target != found_path:
            os.remove(found_path)
    except Exception as exc:
        return False, str(exc)
    return True, "%s: %s" % (action, slug)



# ---------- F&O entry write paths ----------
# Everything here exists so a line that cannot be typed into F&O can be made typeable from the
# page. Two grains, deliberately both: correcting the finalized day fixes the hours you are
# entering now, setting the field on the project or the customer stops the gap coming back.

def _set_block_field(text, header, key, value):
    """Set `key: value` inside a `## Header` block, keeping any trailing `# comment`.

    Replaces the line rather than substituting into it, for the same reason `_apply_fm` does:
    a value is free text and a regex template would rewrite itself. A key not already in the
    block is appended to the end of it."""
    m = re.search(r"^## +%s\s*$(.*?)(?=^## |\Z)" % re.escape(header), text, re.M | re.S)
    if not m:
        return None
    block = m.group(1)
    lines = block.split("\n")
    for i, line in enumerate(lines):
        k = re.match(r"^(%s)\s*:(.*)$" % re.escape(key), line)
        if not k:
            continue
        comment = k.group(2).split("#", 1)
        tail = ("     #" + comment[1]) if len(comment) > 1 else ""
        lines[i] = "%s: %s%s" % (key, value, tail) if value else "%s:%s" % (key, tail)
        return text[:m.start(1)] + "\n".join(lines) + text[m.end(1):]
    body = block.rstrip("\n")
    return text[:m.start(1)] + body + "\n%s: %s\n\n" % (key, value) + text[m.end(1):]


def fno_field(kind, target, key, value):
    """Write one F&O field onto a project's `## Identity` or a customer node's `## Customer`.

    The source fix for a missing dimension: the project that has no `fno_code`, the customer
    whose registration rule was never written down. Nothing else in either file is touched."""
    if key not in FNO_FIELDS:
        return False, "not an F&O field: %r" % (key,)
    value = (value or "").strip()
    if not FNO_VALUE_RE.match(value):
        return False, "value has characters that cannot go on a field line"
    if kind == "project":
        if not re.match(r"^(customers/[^/]+/[^/]+|own/[^/]+)$", target or ""):
            return False, "not a project key: %r" % (target,)
        path, header = os.path.join(ROOT, target.replace("/", os.sep), "CLAUDE.md"), "Identity"
    elif kind == "customer":
        if not re.match(r"^[\w.-]+$", target or ""):
            return False, "not a customer: %r" % (target,)
        path, header = os.path.join(ROOT, "customers", target, "CLAUDE.md"), "Customer"
    else:
        return False, "unknown target kind: %r" % (kind,)
    if not os.path.exists(path):
        return False, "no CLAUDE.md at %s" % target
    text, crlf = _read_raw(path)
    out = _set_block_field(text, header, key, value)
    if out is None:
        return False, "%s has no ## %s block" % (target, header)
    if out == text:
        return True, "%s already %s" % (key, value or "blank")
    try:
        _write_raw(path, out, crlf)
    except Exception as exc:
        return False, str(exc)
    return True, "%s: %s = %s" % (target, key, value or "(blank)")


def _totals_span(lines):
    """(first, last) index of the timesheet table plus its two total lines, or None."""
    head = tail = None
    for i, line in enumerate(lines):
        if head is None and line.startswith("| Project |"):
            head = i
        if line.startswith("**Internal total:"):
            tail = i
    return (head, tail) if head is not None and tail is not None and tail > head else None


def _line_index(rows, row, date):
    """The one line in a day file that `row` names -> (index, "") or (None, why).

    `row` is the line as the page was showing it (project + the three F&O dimensions).
    Anything other than exactly one match means the file moved underneath the page, and
    a write that guessed which line was meant would correct the wrong one."""
    def key(r):
        return (r["project"], (r["proj_id"] or "").strip(),
                (r["activity"] or "").strip(), (r["fno_task"] or "").strip())

    want = (row.get("project") or "", (row.get("proj_id") or "").strip(),
            (row.get("activity") or "").strip(), (row.get("fno_task") or "").strip())
    hits = [i for i, r in enumerate(rows) if key(r) == want]
    if len(hits) == 1:
        return hits[0], ""
    return None, ("that line is no longer in %s -- refresh" % date if not hits
                  else "%d lines in %s match -- correct the file by hand" % (len(hits), date))


def _trail(verb, what, note):
    return "%s from the dashboard %s: %s%s" % (
        verb, datetime.date.today().isoformat(), what,
        (" -- " + re.sub(r"\s+", " ", note).strip()[:300]) if note else "")


def _write_day(path, rows, trail):
    """Re-render a day file's table from `rows` and record the correction underneath.

    The file's own convention (ops/time/README.md) is that a correction says so in the
    file; everything outside the table and the totals is left exactly as it was, so a
    /log review note written by hand survives the write."""
    text, crlf = _read_raw(path)
    lines = text.split("\n")
    span = _totals_span(lines)
    if span is None:
        return False, "%s does not look like a timesheet file" % os.path.basename(path)
    table, _, _ = rollup.render_table(rows)
    body = lines[:span[0]] + table.split("\n") + [""] + [trail] + lines[span[1] + 1:]
    try:
        _write_raw(path, "\n".join(body), crlf)
    except Exception as exc:
        return False, str(exc)
    return True, ""


def timesheet_edit(date, row, updates, note=""):
    """Correct one line of a finalized `ops/time/timesheet/<YYYY-MM>/<date>.md`.

    ops/time/README.md: "Edit this file to correct -- never the heartbeats." This is that edit,
    made from the page instead of by hand, and it keeps the file's own convention of recording
    the correction underneath.

    `row` names the line as the page was showing it (project + the three F&O dimensions); if it
    no longer matches exactly one line the file moved underneath and nothing is written."""
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date or ""):
        return False, "bad date: %r" % (date,)
    path = rollup.daily_path(date)
    if not os.path.exists(path):
        return False, ("%s is not finalized yet -- its hours are still a live tally. "
                       "Run /log or ops/time/rollup.py first." % date)
    rows = rollup.parse_daily_file(date)
    if not rows:
        return False, "%s has no timesheet lines" % date
    idx, why = _line_index(rows, row, date)
    if idx is None:
        return False, why
    target = rows[idx]

    changed = []
    for field_ in ("proj_id", "activity", "fno_task"):
        if field_ not in updates:
            continue
        val = (updates[field_] or "").strip()
        if not FNO_VALUE_RE.match(val):
            return False, "%s has characters that cannot go in the table" % field_
        if val != (target[field_] or ""):
            changed.append("%s %s -> %s" % (field_, target[field_] or "-", val or "-"))
            target[field_] = val
    if "hours" in updates:
        try:
            hrs = round(float(updates["hours"]) * 4) / 4.0
        except (TypeError, ValueError):
            return False, "hours must be a number"
        if not 0 < hrs <= 24:
            return False, "hours out of range"
        if abs(hrs - target["hours"]) > 1e-9:
            changed.append("hours %.2f -> %.2f" % (target["hours"], hrs))
            target["hours"] = hrs
    if not changed:
        return False, "nothing to change"

    ok, err = _write_day(path, rows, _trail("Corrected", "; ".join(changed), note))
    if not ok:
        return False, err
    return True, "%s: %s" % (date, "; ".join(changed))


def timesheet_split(date, row, parts, note=""):
    """Split one line of a finalized day between the work SESSIONS behind it.

    A timesheet day groups by dimension, so three sessions on one customer with nothing
    tagged are one line -- and one line takes one F&O task. But the three were a cluster
    error, a deployment and the Marketo work, and they belong under three different
    tasks. This is the same act as timesheet_edit (rewrite the day file, record the
    correction underneath); it just ends with more lines than it started with.

    Each part carries its hours and the dimensions they move to. What is not claimed
    stays on the original line, so the day's total is unchanged -- a split moves hours
    between lines, it never creates or drops any. The Proj ID is NOT a part's to change:
    it belongs to the project, so every part inherits the line's and one act does one
    thing.

    A part that names its session is also written to the session register
    (ops/lib/sessionlines.py), so the evidence follows the hours. Without it both halves
    of a split line keep showing all three sessions -- the heartbeats are immutable and
    the dimensions they derive have not moved."""
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date or ""):
        return False, "bad date: %r" % (date,)
    if not parts:
        return False, "nothing to split off"
    path = rollup.daily_path(date)
    if not os.path.exists(path):
        return False, ("%s is not finalized yet -- its hours are still a live tally. "
                       "Run /log or ops/time/rollup.py first." % date)
    rows = rollup.parse_daily_file(date)
    if not rows:
        return False, "%s has no timesheet lines" % date
    idx, why = _line_index(rows, row, date)
    if idx is None:
        return False, why
    target = rows[idx]
    home = ((target["activity"] or "").strip(), (target["fno_task"] or "").strip())

    clean, total = [], 0.0
    for p in parts:
        try:
            hrs = round(float(p.get("hours")) * 4) / 4.0
        except (TypeError, ValueError):
            return False, "hours must be a number"
        if hrs <= 0:
            continue
        dims = ((p.get("activity") or "").strip(), (p.get("fno_task") or "").strip())
        for v in dims:
            if not FNO_VALUE_RE.match(v):
                return False, "%r has characters that cannot go in the table" % (v,)
        if dims == home:
            return False, ("one part is going where the line already is -- give it a task "
                           "or an activity of its own")
        clean.append({"session": (p.get("session") or "").strip(), "hours": hrs,
                      "activity": dims[0], "fno_task": dims[1]})
        total = round(total + hrs, 2)
    if not clean:
        return False, "nothing to split off"
    if total > target["hours"] + 1e-9:
        return False, "%.2f h is more than the line has (%.2f h)" % (total, target["hours"])

    # Parts that land on the same dimensions are one line, however they were entered --
    # and so is a line the day already has there.
    same = {}
    for r in rows:
        if r["project"] == target["project"] and r is not target:
            same.setdefault(((r["activity"] or "").strip(), (r["fno_task"] or "").strip()), r)
    want = {}
    for p in clean:
        dims = (p["activity"], p["fno_task"])
        want[dims] = round(want.get(dims, 0.0) + p["hours"], 2)
    moved = []
    for dims in sorted(want):
        hrs = want[dims]
        into = same.get(dims)
        if into is not None:
            into["hours"] = round(into["hours"] + hrs, 2)
        else:
            rows.append({"project": target["project"], "proj_id": target["proj_id"],
                         "activity": dims[0], "fno_task": dims[1], "hours": hrs,
                         "billable": target["billable"]})
        moved.append("%.2f h -> %s" % (hrs, dims[1] or dims[0]))
    left = round(target["hours"] - total, 2)
    if left > 0:
        target["hours"] = left
    else:
        rows.remove(target)

    what = "%s split, %s%s" % (
        target["project"], "; ".join(moved),
        (", %.2f h left where it was" % left) if left > 0 else ", nothing left on it")
    ok, err = _write_day(path, rows, _trail("Split", what, note))
    if not ok:
        return False, err

    # The register is written only after the hours have moved, so it can never claim a
    # split the file does not have.
    for p in clean:
        if p["session"]:
            sessionlines.record(date, p["session"], target["project"],
                                p["activity"], p["fno_task"], note)
    return True, "%s: %s" % (date, "; ".join(moved))


# ---------- Excel ----------
# F&O is fed either by typing or by a sheet, so the period has to be able to leave as a
# workbook. Written with zipfile + string templates for the same reason read_companies reads
# one that way: no dependency, and the format is small enough to be honest about.

XLSX_ESC = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}


def _xl(s):
    return "".join(XLSX_ESC.get(c, c) for c in str(s if s is not None else ""))


def _col(n):
    """0 -> A, 26 -> AA."""
    out = ""
    n += 1
    while n:
        n, r = divmod(n - 1, 26)
        out = chr(65 + r) + out
    return out


def build_xlsx(title, headers, rows):
    """-> xlsx bytes. One sheet; text cells inline, numbers numeric so Excel can sum them."""
    import zipfile
    def cell(c, r, v):
        ref = "%s%d" % (_col(c), r)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return '<c r="%s"><v>%s</v></c>' % (ref, repr(round(float(v), 2)))
        return '<c r="%s" t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>' % (ref, _xl(v))
    body = ['<row r="1">%s</row>' % "".join(cell(i, 1, h) for i, h in enumerate(headers))]
    for n, r in enumerate(rows, start=2):
        body.append('<row r="%d">%s</row>' % (n, "".join(cell(i, n, v) for i, v in enumerate(r))))
    sheet = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
             '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
             '<sheetData>%s</sheetData></worksheet>' % "".join(body))
    parts = {
        "[Content_Types].xml":
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.'
            'relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-'
            'officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/'
            'sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.'
            'spreadsheetml.worksheet+xml"/></Types>',
        "_rels/.rels":
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
            'relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        "xl/workbook.xml":
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="%s" sheetId="1" r:id="rId1"/></sheets></workbook>'
            % _xl(title[:31] or "Sheet1"),
        "xl/_rels/workbook.xml.rels":
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
            'relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>',
        "xl/worksheets/sheet1.xml": sheet,
    }
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in parts.items():
            z.writestr(name, data)
    return buf.getvalue()


ENTRY_COLUMNS = ("Date", "Company", "Customer", "Project", "Proj ID", "Activity", "Task",
                 "Description", "Hours", "Line property", "What it was", "Not ready")


def entry_workbook(req):
    """-> (filename, bytes) for the rows the page is showing.

    The PAGE sends the rows, not a range key: on the week view the hours are the F&O entry
    figure derived from the value model, and a sheet that disagreed with the blocks above it
    would be worse than no sheet at all. What you download is what you see."""
    rows = req.get("rows") or []
    if not isinstance(rows, list) or not rows:
        return None, "nothing to export"
    if len(rows) > 5000:
        return None, "too many rows"
    out = []
    for r in rows:
        if not isinstance(r, dict):
            return None, "bad row"
        out.append([r.get("date", ""), r.get("firma", ""), r.get("customer", ""),
                    (r.get("project", "") or "").replace("customers/", ""),
                    r.get("proj_id", ""), r.get("activity", ""), r.get("fno_task", ""),
                    r.get("description", ""), float(r.get("hours") or 0),
                    "No charge" if r.get("no_charge") else "",
                    r.get("summary", ""),
                    ", ".join(m.get("label", "") for m in (r.get("missing") or []))])
    # The name reaches the browser as Content-Disposition, so it keeps to word characters:
    # a dot run or a separator in a download name is noise at best.
    name = re.sub(r"[^\w-]+", "-", str(req.get("name") or "fno-entry")).strip("-") or "fno-entry"
    return name + ".xlsx", build_xlsx(str(req.get("title") or "F&O entry"),
                                      ENTRY_COLUMNS, out)


# ---------- server ----------

# Three pages, one payload.
PAGES = {"/": "web/today.html", "/index.html": "web/today.html", "/today": "web/today.html",
         "/projects": "web/projects.html", "/time": "web/time.html"}
WEB = os.path.join(HERE, "web")
MIME = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
        ".js": "text/javascript; charset=utf-8", ".json": "application/json; charset=utf-8",
        ".svg": "image/svg+xml", ".ico": "image/x-icon", ".png": "image/png",
        ".woff2": "font/woff2", ".map": "application/json; charset=utf-8"}

# One entry per write path. Each takes the decoded request body and returns (ok, message).
POST_ROUTES = {
    "/api/launch": lambda r: launch(r.get("path", ""), r.get("mode", "claude"),
                                    r.get("prompt", "")),
    "/api/reassign": lambda r: reassign(r.get("date", ""), r.get("row") or {},
                                        r.get("to", ""), r.get("billable"),
                                        r.get("note", "")),
    "/api/noinvoice": lambda r: never_invoice(r.get("date", ""), r.get("row") or {},
                                              r.get("to", ""), r.get("note", "")),
    "/api/fnotask": lambda r: fnotasks.record(r.get("id", ""), r.get("name", ""),
                                              r.get("customer", "")),
    # `activity` / `fno_task` default to None, not "": set-dims writes only what was sent,
    # and an absent key must not blank the field the task already carries.
    "/api/task": lambda r: task_mutate(r.get("slug", ""), r.get("action", ""),
                                       date=r.get("date", ""),
                                       waiting_on=r.get("waiting_on", ""),
                                       text=r.get("text", ""),
                                       activity=r.get("activity"),
                                       fno_task=r.get("fno_task")),
    "/api/todo": lambda r: todo_mutate(r.get("line"), r.get("action", ""), r.get("raw", "")),
    "/api/fno": lambda r: fno_field(r.get("kind", ""), r.get("target", ""),
                                    r.get("field", ""), r.get("value", "")),
    "/api/timesheet": lambda r: timesheet_edit(r.get("date", ""), r.get("row") or {},
                                               r.get("set") or {}, r.get("note", "")),
    "/api/tssplit": lambda r: timesheet_split(r.get("date", ""), r.get("row") or {},
                                              r.get("parts") or [], r.get("note", "")),
}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?", 1)[0]          # a query string is not part of the route
        if self.path.startswith("/api/data"):
            try:
                self._send(200, json.dumps(collect()))
            except Exception as exc:
                self._send(500, json.dumps({"error": str(exc)}))
            return
        if path == "/api/today":
            try:
                self._send(200, json.dumps(collect_daybrief()))
            except Exception as exc:
                self._send(500, json.dumps({"error": str(exc)}))
            return
        if path in PAGES:
            self._send_file(os.path.join(HERE, PAGES[path]))
            return
        if path.startswith("/web/"):
            self._send_file(os.path.join(WEB, path[len("/web/"):]))
            return
        self._send(404, "not found", "text/plain")

    def _send_file(self, path):
        """Serve one file from disk, refusing anything outside ops/."""
        full = os.path.abspath(path)
        if not full.startswith(os.path.abspath(HERE) + os.sep):
            self._send(403, "forbidden", "text/plain")
            return
        try:
            with open(full, "rb") as f:
                body = f.read()
        except Exception:
            self._send(404, os.path.basename(full) + " not found", "text/plain")
            return
        ctype = MIME.get(os.path.splitext(full)[1].lower(), "application/octet-stream")
        self._send(200, body, ctype)

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/xlsx":
            try:
                n = int(self.headers.get("Content-Length") or 0)
                name, body = entry_workbook(json.loads(self.rfile.read(n) or b"{}"))
            except Exception as exc:
                self._send(500, json.dumps({"ok": False, "message": str(exc)}))
                return
            if name is None:
                self._send(400, json.dumps({"ok": False, "message": body}))
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/vnd.openxmlformats-officedocument."
                                             "spreadsheetml.sheet")
            self.send_header("Content-Disposition", 'attachment; filename="%s"' % name)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return
        handler = POST_ROUTES.get(path)
        if handler is None:
            self._send(404, "{}")
            return
        try:
            n = int(self.headers.get("Content-Length") or 0)
            req = json.loads(self.rfile.read(n) or b"{}")
            ok, msg = handler(req)
            if ok:
                invalidate()        # a write must not sit behind the payload memo
            self._send(200 if ok else 400, json.dumps({"ok": ok, "message": msg}))
        except Exception as exc:
            self._send(500, json.dumps({"ok": False, "message": str(exc)}))

    def log_message(self, *args):
        pass


def serve(open_browser=True):
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = "http://127.0.0.1:%d/" % PORT
    print("Dashboard at %s  (Ctrl+C to stop)" % url)
    if open_browser:
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception:
            pass
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    if "--json" in sys.argv:
        print(json.dumps(collect(), indent=2))
    else:
        serve(open_browser="--no-open" not in sys.argv)
