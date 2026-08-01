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


def memory_index():
    """{session8: [(yyyymmdd, first-user-line), ...]} from ops/memory/daily/.

    The turn-hook writes `id: <utc-ts>Z-<session8>` above each record, which is the only join
    between a heartbeat and what was actually being said in it."""
    idx = {}
    pat = re.compile(
        r"id: (\d{8})T\d{6}Z-([0-9a-f]{6,12})\n.*?\n---\n\n\*\*User:\*\* (.*?)\n", re.S)
    for path in sorted(glob.glob(os.path.join(ROOT, "ops", "memory", "daily", "*.md"))):
        for day, sess, line in pat.findall(read(path)):
            txt = plain(line)
            # Skip harness noise (~10% of turns): a skill's injected preamble, a background-task
            # notification, raw tool output echoed back. None of it says what the work WAS.
            if (not txt or txt.startswith("Base directory for this skill")
                    or txt.startswith("<") or "task-notification" in txt[:40]):
                continue
            idx.setdefault(sess, []).append((day, txt[:220]))
    return idx


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
            rows.append({"date": date, "session": sess, "project": proj, "hours": hours,
                         "turns": len(sub), "co": co, "evidence": ev,
                         "scope": "dev" if proj == "Dev" else "own"})
    rows.sort(key=lambda r: (not r["co"], r["date"], -r["hours"]))
    return rows


def last_heartbeat_by_session():
    """{session8: last ts_end (UTC datetime)} -- the only evidence a tagged session still exists."""
    seen = {}
    for hb in rollup.load_heartbeats():
        s = (hb.get("session") or "")[:8]
        if s and (s not in seen or hb["end"] > seen[s]):
            seen[s] = hb["end"]
    return seen


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
        if self.path.startswith("/api/data"):
            try:
                self._send(200, json.dumps(collect()))
            except Exception as exc:
                self._send(500, json.dumps({"error": str(exc)}))
            return
        if self.path in ("/", "/index.html"):
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
