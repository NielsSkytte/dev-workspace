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

The served page re-fetches /api/data on every load and on Refresh, so it is never stale.
POST /api/launch starts a new Claude Code session (or VS Code window) rooted at a project --
which is also what makes that session's time attribute to the right project.

Pure stdlib, ASCII-only (workspace convention).
"""
import os, sys, re, json, glob, datetime, subprocess, shutil, importlib.util
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

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


# ---------- small parsers ----------

def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def parse_identity(text):
    """The `## Identity` block of a project CLAUDE.md -> {key: value}."""
    out = {}
    block = re.search(r"^## Identity\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not block:
        return out
    for line in block.group(1).splitlines():
        m = re.match(r"^([a-z_]+):(.*)$", line.strip())
        if m:
            val = m.group(2).split("#", 1)[0].strip()
            out[m.group(1)] = val
    return out


def parse_frontmatter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        k = re.match(r"^([a-z_]+):(.*)$", line.strip())
        if k:
            out[k.group(1)] = k.group(2).split("#", 1)[0].strip()
    return out


def sections(text):
    """-> {heading: body} for every `## Heading` in a markdown file."""
    out, cur, buf = {}, None, []
    for line in text.splitlines():
        m = re.match(r"^## +(.+?)\s*$", line)
        if m:
            if cur:
                out[cur] = "\n".join(buf).strip()
            cur, buf = m.group(1), []
        elif cur:
            buf.append(line)
    if cur:
        out[cur] = "\n".join(buf).strip()
    return out


def bullets(body, limit=6):
    """Leading bullet / numbered items of a section body, markdown stripped to plain text."""
    out = []
    for line in (body or "").splitlines():
        s = line.strip()
        m = re.match(r"^(?:[-*]|\d+\.)\s+(.*)$", s)
        if m:
            item = m.group(1).strip()
            if item.startswith("~~"):
                continue          # struck through = resolved; not an open item
            out.append(plain(item))
    return out[:limit]


def labelled(body, label):
    """Bullets that follow a `**Label:**` line, up to the next bold label or blank run."""
    if not body:
        return []
    lines = body.splitlines()
    out, grabbing = [], False
    for line in lines:
        s = line.strip()
        if re.match(r"^\*\*.+?:\*\*", s):
            grabbing = s.lower().startswith("**" + label.lower())
            rest = re.sub(r"^\*\*.+?:\*\*", "", s).strip()
            if grabbing and rest:
                out.append(plain(rest))
            continue
        if grabbing:
            m = re.match(r"^(?:[-*]|\d+\.)\s+(.*)$", s)
            if m:
                out.append(plain(m.group(1)))
            elif not s:
                continue
    return out[:6]


def field(body, label):
    """The value of a `**Label:** value` line."""
    m = re.search(r"^\*\*" + re.escape(label) + r":\*\*\s*(.+)$", body or "", re.M)
    return plain(m.group(1)) if m else ""


def plain(s):
    s = re.sub(r"`([^`]*)`", r"\1", s)
    s = re.sub(r"\*\*([^*]*)\*\*", r"\1", s)
    s = re.sub(r"~~([^~]*)~~", r"\1", s)
    s = re.sub(r"\[\[([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    return s.strip()


def first_para(body, limit=420):
    for para in (body or "").split("\n\n"):
        p = plain(" ".join(x.strip() for x in para.splitlines()).strip())
        if p and not p.startswith("---"):
            return p[:limit] + ("..." if len(p) > limit else "")
    return ""


def iso_days_ago(date_str, today):
    try:
        d = datetime.date.fromisoformat(date_str[:10])
    except Exception:
        return None
    return (datetime.date.fromisoformat(today) - d).days


# ---------- discovery ----------

def discover():
    """-> (projects, customers). A project is a folder with its own CLAUDE.md."""
    projects, customers = {}, {}

    for cdir in sorted(glob.glob(os.path.join(ROOT, "customers", "*"))):
        if not os.path.isdir(cdir):
            continue
        cname = os.path.basename(cdir)
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
        for pdir in sorted(glob.glob(os.path.join(cdir, "*"))):
            if os.path.isdir(pdir) and os.path.exists(os.path.join(pdir, "CLAUDE.md")):
                key = "customers/%s/%s" % (cname, os.path.basename(pdir))
                projects[key] = build_project(key, pdir, cname)
                customers[cname]["projects"].append(key)

    for pdir in sorted(glob.glob(os.path.join(ROOT, "own", "*"))):
        if os.path.isdir(pdir) and os.path.exists(os.path.join(pdir, "CLAUDE.md")):
            key = "own/" + os.path.basename(pdir)
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
    ident = parse_identity(read(os.path.join(pdir, "CLAUDE.md")))
    ctx = sections(read(os.path.join(pdir, "CONTEXT.md")))
    state = ctx.get("State", "")
    return {
        "key": key, "name": os.path.basename(pdir), "customer": customer, "path": pdir,
        "billable": key.startswith("customers/"),
        "fno_code": ident.get("fno_code", "") or "UNSET",
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
            fm = parse_frontmatter(text)
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

AUDIT_WEEKS = 8          # how many ISO weeks back the page can page through
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


def collect_audit(today):
    """-> {weeks: [...], byWeek: {wk: {...}}} -- one fully-categorised block per ISO week."""
    hbs = rollup.load_heartbeats()
    hbs_by_date = {}
    for hb in hbs:
        hbs_by_date.setdefault(hb["date"], []).append(hb)
    absence = rollup.load_absence()

    cur = datetime.date.fromisoformat(today)
    monday = cur - datetime.timedelta(days=cur.weekday())
    weeks, by_week = [], {}
    for back in range(AUDIT_WEEKS):
        m = monday - datetime.timedelta(days=7 * back)
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

        # per F&O line: the timesheet row is the claim, the value record is the evidence beside it
        sheet = rollup.parse_daily_file(d)
        claim_by, meas_by = {}, {}
        for r in (sheet if sheet is not None else rollup.rows_for(dh)):
            claim_by[_dimkey(r["project"], r["activity"], r["fno_task"])] = r
        for r in rollup.rows_for(dh):
            meas_by[_dimkey(r["project"], r["activity"], r["fno_task"])] = r["hours"]
        agg = {}
        for v in vals:
            _fold(agg.setdefault(_dimkey(v["project"], v.get("activity"), v.get("fno_task")),
                                 _blank_agg()), v)
        for k in sorted(set(claim_by) | set(agg)):
            r = claim_by.get(k)
            a = agg.get(k) or _blank_agg()
            project, activity, fno_task = k.split("|", 2)
            lines.append({
                "date": d, "project": project, "activity": activity, "fno_task": fno_task,
                "proj_id": r["proj_id"] if r else rollup.project_id(project),
                "billable": r["billable"] if r else project.startswith("customers/"),
                "claimed": r["hours"] if r else 0.0,
                "measured": meas_by.get(k, 0.0),
                "keyboard": round(a["keyboard"], 2), "weighted": round(a["weighted"], 2),
                "turns": a["turns"], "stretches": a["stretches"], "t5": a["t5"],
                "tiers": a["tiers"], "files": len(a["files"]),
                "topFiles": [os.path.basename(p) for p in sorted(a["files"])[:4]],
                "live": sheet is None,
            })

    tot = lambda f: round(sum(x[f] for x in days), 2)
    claimed = tot("claimed")
    return {
        "week": wk, "start": dates[0], "end": dates[6],
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
TIP_BLOCKS = 4           # sessions shown before the hover says "+N more"


def _says_something(text):
    """A turn worth showing in a hover: long enough, and actually words.

    A markdown rule ("---------") or a row of dashes clears a length test but says nothing."""
    return (len(text) >= MIN_TURN_CHARS
            and sum(c.isalnum() for c in text) >= 8)


def collect_line_sessions(today):
    """{'<date>|<project>|<activity>|<task>': [{session, turns, hours, task, lines[]}]} (lowercased key)."""
    cutoff = str(datetime.date.fromisoformat(today) - datetime.timedelta(weeks=SESSION_WEEKS))
    mem = memory_index()
    by = {}
    for hb in rollup.load_heartbeats():
        if hb["date"] < cutoff:
            continue
        activity, fno_task = rollup.task_dims(hb.get("task"))
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
            blocks.append({
                "session": sess or "(no session id)",
                "turns": len(group),
                "hours": round(sum(r["hours"] for r in rollup.rows_for(group)), 2),
                "task": slugs[0] if len(slugs) == 1 else ("; ".join(slugs) if slugs else ""),
                "lines": lines,
            })
        blocks.sort(key=lambda b: -b["hours"])
        # The hover is a summary, not a transcript: keep the biggest sessions and count the rest.
        out[key] = {"blocks": blocks[:TIP_BLOCKS], "total": len(blocks),
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
CUSTOMER_ALIASES = {
    "jtj": "joeandthejuice",
    # Typo in the source sheet: it reads "Vestforbraeding", missing the n after ae
    # (correct Danish is Vestforbraending). Aliased so the entry page works; fix the xlsx and
    # this line becomes dead.
    "vestforbraeding": "vestforbraending",
}


def _norm_customer(name):
    s = (name or "").strip().lower()
    for a, b in (("æ", "ae"), ("ø", "oe"), ("å", "aa"),
                 ("Æ", "ae"), ("Ø", "oe"), ("Å", "aa")):
        s = s.replace(a, b)
    s = re.sub(r"[\s\-_/.]", "", s)
    return CUSTOMER_ALIASES.get(s, s)


def read_companies():
    """Parse ops/TidsregInfo.xlsx -> [{firma, kunde, projektnr, aktivitet, task_note}].

    Read straight from the workbook (stdlib zipfile + ElementTree, no openpyxl) so the owner's
    own sheet stays the single source for the internal-company grouping -- edit the xlsx and the
    dashboard follows, with no exported copy to drift."""
    # Resolve case-insensitively: the file is TidsregInfo.xlsx on disk and Windows does not care,
    # but a hard-coded lowercase path would break anywhere else.
    folder = os.path.join(ROOT, "ops")
    path = ""
    try:
        for name in os.listdir(folder):
            if name.lower() == "tidsreginfo.xlsx":
                path = os.path.join(folder, name)
                break
    except OSError:
        return []
    if not path:
        return []
    ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    try:
        import zipfile, xml.etree.ElementTree as ET
        z = zipfile.ZipFile(path)
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")):
                shared.append("".join(t.text or "" for t in si.iter(ns + "t")))
        grid = []
        for row in ET.fromstring(z.read("xl/worksheets/sheet1.xml")).iter(ns + "row"):
            cells = {}
            for c in row.iter(ns + "c"):
                ref = re.match(r"([A-Z]+)", c.get("r") or "A")
                col = 0
                for ch in (ref.group(1) if ref else "A"):
                    col = col * 26 + (ord(ch) - 64)
                v = c.find(ns + "v")
                txt = ""
                if c.get("t") == "s" and v is not None:
                    idx = int(v.text)
                    txt = shared[idx] if idx < len(shared) else ""
                elif c.get("t") == "inlineStr":
                    txt = "".join(t.text or "" for t in c.iter(ns + "t"))
                elif v is not None:
                    txt = v.text or ""
                cells[col - 1] = txt.strip()
            grid.append([cells.get(i, "") for i in range(max(cells) + 1)] if cells else [])
    except Exception:
        return []

    out = []
    for row in grid[1:]:                       # row 0 is the header
        row = row + [""] * 5
        firma, kunde = row[0].strip(), row[1].strip()
        if not firma or not kunde:
            continue
        out.append({"firma": firma, "kunde": kunde, "key": _norm_customer(kunde),
                    "projektnr": row[2].strip(), "aktivitet": row[3].strip(),
                    "task_note": row[4].strip()})
    return out


def collect_entry(entries, customers, today):
    """F&O entry rows: one per date/customer/project/activity/task, tagged with the internal
    company (Firma). F&O takes one timesheet PER COMPANY, so the company is the outermost grouping
    on the page -- it is the thing you open a separate sheet for.

    Returned FLAT (every date, not pre-bucketed) so the timesheet page can slice any range --
    a month, last week, the week before -- without the collector knowing which."""
    comp = read_companies()
    by_key = {c["key"]: c for c in comp}
    ws_keys = {_norm_customer(c): c for c in customers}

    def decorate(e, agg, unmapped):
        """One timesheet entry -> one F&O entry row (company, customer, resolved Proj ID)."""
        p = e["project"]
        cust = p.split("/")[1] if p.lower().startswith("customers/") and "/" in p else ""
        row_c = by_key.get(_norm_customer(cust)) if cust else None
        if cust and row_c is None:
            unmapped[cust] = round(unmapped.get(cust, 0.0) + e["hours"], 2)
        firma = row_c["firma"] if row_c else ("" if cust else "INTERNAL")

        # Proj ID: the timesheet's own value wins; the sheet fills a gap; disagreement is flagged,
        # never silently resolved.
        ws_id = e["proj_id"]
        xl_id = row_c["projektnr"] if row_c else ""
        weak = (not ws_id) or ws_id in ("UNSET", "") or ws_id.startswith("PENDING")
        proj_id = (xl_id or ws_id) if weak else ws_id
        conflict = bool(xl_id and not weak and xl_id != ws_id)
        activity = e["activity"] or (row_c["aktivitet"] if row_c else "")

        k = (firma, e["date"], cust, p, proj_id, activity, e["fno_task"])
        cell = agg.setdefault(k, {"firma": firma, "date": e["date"], "customer": cust,
                                  "project": p, "proj_id": proj_id, "activity": activity,
                                  "fno_task": e["fno_task"], "hours": 0.0,
                                  "from_sheet": weak and bool(xl_id), "conflict": conflict,
                                  "ws_proj_id": ws_id, "task_note": row_c["task_note"] if row_c else ""})
        cell["hours"] = round(cell["hours"] + e["hours"], 2)

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
    for key, first, last in (
            ("month0", d0.replace(day=1), None),
            ("month1", (d0.replace(day=1) - datetime.timedelta(days=1)).replace(day=1), None),
            ("week1", d0 - datetime.timedelta(days=7 + d0.weekday()), 7),
            ("week2", d0 - datetime.timedelta(days=14 + d0.weekday()), 7)):
        if last is None:                       # whole calendar month
            nxt = (first.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
            span = (nxt - first).days
        else:
            span = last
        ranges[key] = [(first + datetime.timedelta(days=i)).isoformat() for i in range(span)]

    merged = {}
    for key, dates in ranges.items():
        inr = set(dates)
        src = [e for e in entries if e["date"] in inr]
        if not src:
            merged[key] = []
            continue
        merged[key] = build(rollup.consolidate_week(src, dates, ENTRY_MERGE_THRESHOLD))[0]

    return {
        "rows": rows,
        "merged": merged,
        "ranges": ranges,
        "companies": sorted({c["firma"] for c in comp}),
        "mapping": comp,
        "unmapped": sorted(({"customer": k, "hours": v} for k, v in unmapped.items()),
                           key=lambda x: -x["hours"]),
        "no_project": sorted(c["kunde"] for c in comp if c["key"] not in ws_keys),
    }


def active_sessions():
    """Task tags recorded in ops/time/active-task, each marked live or stale.

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
    return [o for o in out if o["slug"]]


def collect_todos():
    text = read(os.path.join(ROOT, "ops", "TODO.md"))
    open_items = []
    for line in text.splitlines():
        m = re.match(r"^- \[ \]\s*(\d{4}-\d{2}-\d{2})?\s*[-\u2014]?\s*(.*)$", line.strip())
        if m:
            open_items.append({"date": m.group(1) or "", "text": plain(m.group(2))[:300]})
    return open_items


# ---------- assembly ----------

def collect():
    today = rollup.to_local(datetime.datetime.now(datetime.timezone.utc)).strftime("%Y-%m-%d")
    projects, customers = discover()
    tasks = collect_tasks()
    entries, unfinalized = collect_time(today)
    todos = collect_todos()
    for t in todos:
        t["age"] = iso_days_ago(t["date"], today) if t["date"] else None

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
        age = iso_days_ago(e["date"], today)
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
        p["days_idle"] = iso_days_ago(last, today) if last else None
        p["tasks"] = [t["slug"] for t in tasks_by_project.get(key, [])
                      if t["state"] in ("open", "in-progress")]
        p["tasks_done"] = len([t for t in tasks_by_project.get(key, []) if t["state"] == "done"])

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
        c["days_idle"] = iso_days_ago(c["last_activity"], today) if c["last_activity"] else None
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
        "entry": collect_entry(entries, customers, today),
        "audit": collect_audit(today),
        "lineSessions": collect_line_sessions(today),
        "active_sessions": active_sessions(),
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


# ---------- server ----------

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
        if path in ("/", "/index.html"):
            html = read(os.path.join(HERE, "dashboard.html"))
            if not html:
                self._send(500, "dashboard.html not found", "text/plain")
                return
            self._send(200, html, "text/html; charset=utf-8")
            return
        self._send(404, "not found", "text/plain")

    def do_POST(self):
        if not self.path.startswith("/api/launch"):
            self._send(404, "{}")
            return
        try:
            n = int(self.headers.get("Content-Length") or 0)
            req = json.loads(self.rfile.read(n) or b"{}")
            ok, msg = launch(req.get("path", ""), req.get("mode", "claude"),
                             req.get("prompt", ""))
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
