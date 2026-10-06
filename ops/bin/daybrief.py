#!/usr/bin/env python
"""Day brief -- one derived view of the work, from the substrate the workspace already keeps.

Reads (never invents):
  ops/tasks/open + in-progress      the task files: frontmatter + Progress block + Needs from customer
  <project>/CONTEXT.md              the resume card (Goal, "Where we stand -- <date>", Blocked on others)
  ops/time/heartbeats/*.jsonl       last worked per project
  ops/memory/store/*.md             records scoped to the project (gists)
  ops/TODO.md                       unchecked captures (workspace scope)

Emits, from the same model:
  --text  [--scope S]   the brief a session starts with (ASCII, compact); S = Dev | customers/<C> |
                        customers/<C>/<P> | own/<P>; default Dev
  --json                the model, for the dashboard
  --write-cards [--project P]   regenerate the "## Active tasks -- progress" section of every
                        card-shaped CONTEXT.md from the task files (idempotent); the rest of the
                        card is hand-written at handoff
  --check               which projects carry a card, a legacy CONTEXT.md, or none

Rules it applies (documented in AGENTS.md > Continuity loop, this is the executor):
  progress age  = today - the task's `**Now (YYYY-MM-DD):**` date; falls back to the last Log date,
                  then `created`
  parked        = `waiting_on` set (not "none") or `resume_on` after today
  due back      = `resume_on` on or before today (shown, then cleared by hand)
  unsent ask    = `customer_ask: open`
  stalled       = in progress, not parked, progress age > STALLED_DAYS

Pure stdlib. ASCII output. Writes nothing except the generated card section on --write-cards.
"""
import os, re, sys, json, glob, datetime, argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.substrate import (read, frontmatter, identity, section, clean,
                           first_sentence, parse_date, bullets_joined)
from lib.workspace import identity_file, project_dirs

ROOT = os.environ.get("DEV_WORKSPACE", r"C:\Dev")
TASKS = os.path.join(ROOT, "ops", "tasks")
STORE = os.path.join(ROOT, "ops", "memory", "store")
HEART = os.path.join(ROOT, "ops", "time", "heartbeats")
TODO = os.path.join(ROOT, "ops", "TODO.md")
DASHBOARD_URL = os.environ.get("DASHBOARD_URL", "http://127.0.0.1:8787/")
STALLED_DAYS = 14
WARN_DAYS = 7
GISTS = 5
SECTION_RE = re.compile(r"^## Active tasks (?:—|-|--) progress\s*$", re.M)

_REPL = {"\u2014": "-", "\u2013": "-", "\u2192": "->", "\u00d7": "x", "\u2026": "...",
         "\u201c": '"', "\u201d": '"', "\u2018": "'", "\u2019": "'", "\u00a0": " "}


def asciify(s):
    for k, v in _REPL.items():
        s = s.replace(k, v)
    return s.encode("ascii", "replace").decode("ascii")


def today_local():
    return datetime.date.today()


# ---------------------------------------------------------------- tasks

def parse_task(path, state, today):
    text = read(path)
    fm, body = frontmatter(text)
    slug = os.path.basename(path)[:-3]
    t = {"slug": slug, "state": state, "path": path,
         "title": fm.get("title", ""), "project": fm.get("project", ""),
         "owner": fm.get("owner", ""), "priority": fm.get("priority", ""),
         "fno_task": fm.get("fno_task", ""), "activity": fm.get("activity", ""),
         "customer_ask": (fm.get("customer_ask", "") or "").lower(),
         "waiting_on": fm.get("waiting_on", ""), "resume_on": fm.get("resume_on", ""),
         "blocked_by": fm.get("blocked_by", ""), "created": fm.get("created", "")}
    prog = section(body, "Progress")
    t["has_progress"] = bool(prog.strip())
    m = re.search(r"\*\*Now \((\d{4}-\d{2}-\d{2})\):\*\*\s*(.*?)(?=\n\s*\n|\n\*\*|\Z)", prog, re.S)
    t["now_date"] = m.group(1) if m else ""
    t["now"] = clean(m.group(2)) if m else ""
    m = re.search(r"\*\*Next:\*\*\s*(.*?)(?=\n\s*\n\*\*|\n## |\Z)", prog, re.S)
    nxt = bullets_joined(m.group(1)) if m else []
    if not nxt and m:
        nxt = [clean(m.group(1), 200)] if clean(m.group(1)) else []
    t["next"] = nxt
    t["needs"] = [b for b in bullets_joined(section(body, "Needs from customer")) if b.lower() not in ("none.", "none")]
    logdates = re.findall(r"^\s*-\s*(\d{4}-\d{2}-\d{2})", section(body, "Log"), re.M)
    t["last_log_date"] = max(logdates) if logdates else ""
    pdate = parse_date(t["now_date"]) or parse_date(t["last_log_date"]) or parse_date(t["created"])
    t["progress_date"] = pdate.isoformat() if pdate else ""
    t["progress_age"] = (today - pdate).days if pdate else None
    wo = (t["waiting_on"] or "").strip()
    ro = parse_date(t["resume_on"]) if t["resume_on"] else None
    t["waiting"] = wo if wo and wo.lower() != "none" else ""
    t["due_back"] = bool(ro and ro <= today and not t["waiting"])
    t["parked"] = bool(t["waiting"] or (ro and ro > today))
    t["devops"] = "none" if (t["fno_task"] or "").lower() in ("", "none") else t["fno_task"]
    t["ask_unsent"] = t["customer_ask"] == "open"
    t["stalled"] = (state == "in-progress" and not t["parked"] and t["progress_age"] is not None
                    and t["progress_age"] > STALLED_DAYS)
    return t


def load_tasks(today):
    out = []
    for state in ("in-progress", "open"):
        for p in sorted(glob.glob(os.path.join(TASKS, state, "*.md"))):
            if os.path.basename(p).startswith("_"):
                continue
            out.append(parse_task(p, state, today))
    return out


# ---------------------------------------------------------------- projects and cards

def parse_card(path):
    text = read(path)
    if not text:
        return {"shape": "none"}
    if re.search(r"^## Goal\s*$", text, re.M) and re.search(r"^## Where we stand", text, re.M):
        goal = section(text, "Goal")
        goal = re.split(r"\n\*\*Done when", goal)[0]
        m = re.search(r"^## Where we stand (?:—|-|--)\s*(\d{4}-\d{2}-\d{2})", text, re.M)
        blocked = bullets_joined(section(text, "Blocked on others"))
        who = []
        for b in blocked:
            mm = re.match(r"([^:]{2,40}):", b)
            if mm:
                who.append(mm.group(1).strip())
        return {"shape": "card", "goal": first_sentence(goal), "standing_date": m.group(1) if m else "",
                "blocked_on": who, "open_threads": len(bullets_joined(section(text, "Open threads")))}
    focus = section(text, "Current Focus")
    m = re.search(r"\*\*Last worked:\*\*\s*(\d{4}-\d{2}-\d{2})", text)
    return {"shape": "legacy", "goal": first_sentence(focus) if focus.strip() else "",
            "standing_date": m.group(1) if m else "", "blocked_on": [], "open_threads": 0,
            "bytes": len(text)}


def load_projects():
    out = []
    for key, d in project_dirs(ROOT):
        ident = identity(read(identity_file(d)))
        if not ident:
            continue  # an identity file without an Identity block declares a non-project (a wiki mirror)
        card = parse_card(os.path.join(d, "CONTEXT.md"))
        out.append({"key": key, "status": ident.get("status", ""), "fno_code": ident.get("fno_code", ""),
                    "type": ident.get("type", ""), "card": card})
    return out


def last_worked():
    seen = {}
    for p in sorted(glob.glob(os.path.join(HEART, "*.jsonl")), reverse=True)[:90]:   # ~3 months is enough for "last worked"
        day = os.path.basename(p)[:10]
        try:
            with open(p, encoding="utf-8") as f:
                for line in f:
                    try:
                        proj = json.loads(line).get("project")
                    except Exception:
                        continue
                    if proj and proj not in seen:
                        seen[proj] = day
        except Exception:
            continue
    return seen


def store_gists(project, limit=GISTS):
    cust = project.split("/")[1] if project.lower().startswith("customers/") and "/" in project else ""
    wanted = {"project:" + project, project}
    if cust:
        wanted.add("client:" + cust)
    recs = []
    for p in glob.glob(os.path.join(STORE, "*.md")):
        if os.path.basename(p) == "MEMORY.md":
            continue
        fm, _ = frontmatter(read(p))
        if (fm.get("scope") or "") in wanted:
            recs.append((fm.get("ts", ""), fm.get("id", os.path.basename(p)[:-3]),
                         (fm.get("description", "") or "").strip('"')))
    recs.sort(reverse=True)
    return [{"ts": ts[:10], "id": rid, "gist": g} for ts, rid, g in recs[:limit]]


def todo_open():
    lines = [l for l in read(TODO).split("\n") if re.match(r"^\s*- \[ \]", l)]
    dates = [d for l in lines for d in re.findall(r"20\d\d-\d\d-\d\d", l)[:1]]
    return {"count": len(lines), "oldest": min(dates) if dates else ""}


# ---------------------------------------------------------------- model

def build(today=None):
    today = today or today_local()
    tasks = load_tasks(today)
    projects = load_projects()
    lw = last_worked()
    byproj = {}
    for t in tasks:
        byproj.setdefault(t["project"] or "", []).append(t)
    for p in projects:
        p["last_worked"] = lw.get(p["key"], "")
        p["tasks"] = sorted(byproj.get(p["key"], []),
                            key=lambda t: (t["state"] != "in-progress", t["parked"], -(t["progress_age"] or 0) * -1))
        p["counts"] = summarize(p["tasks"])
    return {"today": today.isoformat(), "weekday": today.strftime("%a"),
            "projects": projects, "workspace_tasks": byproj.get("", []),
            "todo": todo_open(), "dashboard": DASHBOARD_URL}


def summarize(tasks):
    return {"in_progress": sum(1 for t in tasks if t["state"] == "in-progress" and not t["parked"]),
            "open": sum(1 for t in tasks if t["state"] == "open" and not t["parked"]),
            "parked": sum(1 for t in tasks if t["parked"]),
            "due_back": sum(1 for t in tasks if t["due_back"]),
            "stalled": sum(1 for t in tasks if t["stalled"]),
            "asks_unsent": sum(1 for t in tasks if t["ask_unsent"]),
            "devops": sum(1 for t in tasks if t["devops"] != "none"),
            "total": len(tasks)}


# ---------------------------------------------------------------- text

def age(t):
    a = t["progress_age"]
    return "  ?" if a is None else ("%3d" % a)


def task_line(t, width=78):
    flags = []
    if t["ask_unsent"]:
        flags.append("ASK UNSENT")
    if t["stalled"]:
        flags.append("STALLED")
    if t["due_back"]:
        flags.append("DUE BACK " + t["resume_on"])
    if t["parked"]:
        flags.append("waiting on " + t["waiting"] if t["waiting"] else "resumes " + t["resume_on"])
    nxt = ("next: " + t["next"][0]) if t["next"] else ("no Progress block" if not t["has_progress"] else "no next step")
    head = "%s d  %s [%s]" % (age(t), t["slug"], t["devops"])
    tail = (" ".join(flags) + "  " if flags else "") + nxt
    if len(tail) > width:
        tail = tail[:width - 3].rstrip() + "..."
    return head + "  " + tail


def render_project(m, p):
    c = p["card"]; k = p["counts"]
    lines = ["[Day brief] %s %s | %s | last worked %s | standing dated %s%s" % (
        m["weekday"], m["today"], p["key"], p["last_worked"] or "-", c.get("standing_date") or "-",
        (" (%d d)" % (parse_date(m["today"]) - parse_date(c["standing_date"])).days) if c.get("standing_date") else "")]
    if c.get("shape") == "legacy":
        lines.append("CONTEXT.md is the old shape (%d bytes) - run /checkin to convert it to the card." % c.get("bytes", 0))
    if c.get("goal"):
        lines.append("Goal: " + c["goal"])
    lines.append("Tasks: %d in progress, %d open, %d parked, %d due back | stalled >%d d: %d | customer asks unsent: %d | DevOps id: %d of %d" % (
        k["in_progress"], k["open"], k["parked"], k["due_back"], STALLED_DAYS, k["stalled"], k["asks_unsent"], k["devops"], k["total"]))
    groups = [("In progress (progress age, days):", [t for t in p["tasks"] if t["state"] == "in-progress" and not t["parked"]]),
              ("Open:", [t for t in p["tasks"] if t["state"] == "open" and not t["parked"]]),
              ("Parked:", [t for t in p["tasks"] if t["parked"]])]
    for title, ts in groups:
        if ts:
            lines.append(title)
            lines += ["  " + task_line(t) for t in ts]
    if c.get("blocked_on"):
        lines.append("Blocked on others: " + ", ".join(c["blocked_on"]))
    g = store_gists(p["key"])
    if g:
        lines.append("Project memory (%d newest of the store, grep ops/memory/store for more):" % len(g))
        lines += ["  %s  %s - %s" % (x["ts"], x["id"], clean(x["gist"], 110)) for x in g]
    lines.append("Do: /switch-task <slug> before working (customer projects); /task postpone <slug> <date> | "
                 "/task wait <slug> customer | /task resume <slug>; /handoff at the end. Overview: " + m["dashboard"])
    return "\n".join(lines)


def render_workspace(m, only=None):
    ps = [p for p in m["projects"] if p["status"] in ("active", "planned") or p["tasks"]]
    if only:
        ps = [p for p in ps if p["key"].lower().startswith(only.lower() + "/")]
    ps.sort(key=lambda p: p["last_worked"] or "", reverse=True)
    lines = ["[Day brief] %s %s | %s" % (m["weekday"], m["today"], only or "workspace")]
    lines.append("%-44s %-10s %-10s %-9s %-7s %-4s %s" % ("project", "worked", "standing", "tasks", "stalled", "asks", "card"))
    for p in ps:
        c = p["card"]; k = p["counts"]
        lines.append("%-44s %-10s %-10s %-9s %-7s %-4s %s" % (
            p["key"][:44], p["last_worked"] or "-", c.get("standing_date") or "-",
            "%d ip/%d op" % (k["in_progress"], k["open"]) + ("/%dpk" % k["parked"] if k["parked"] else ""),
            str(k["stalled"]) if k["stalled"] else "-", str(k["asks_unsent"]) if k["asks_unsent"] else "-",
            c.get("shape", "none")))
    due = [t for p in ps for t in p["tasks"] if t["due_back"]]
    if due:
        lines.append("Due back today: " + ", ".join(t["slug"] for t in due))
    if not only and m["workspace_tasks"]:
        lines.append("Workspace-level tasks: " + "; ".join("%s (%s)" % (t["slug"], t["state"]) for t in m["workspace_tasks"]))
    if not only:
        lines.append("TODO: %d unchecked%s" % (m["todo"]["count"], (", oldest " + m["todo"]["oldest"]) if m["todo"]["oldest"] else ""))
    lines.append("Overview: " + m["dashboard"] + "  |  open a project session from there, or cd into the project and start one.")
    return "\n".join(lines)


def render_text(scope, m=None):
    m = m or build()
    scope = (scope or "Dev").replace("\\", "/").strip("/")
    for p in m["projects"]:
        if p["key"].lower() == scope.lower():
            return asciify(render_project(m, p))
    if scope.lower().startswith("customers/") and scope.count("/") == 1:
        return asciify(render_workspace(m, only=scope))
    return asciify(render_workspace(m))


# ---------------------------------------------------------------- card section

def render_section(p, today):
    k = p["counts"]
    out = ["<!-- generated by ops/bin/daybrief.py --write-cards on %s from ops/tasks; edit the task files, not this section -->" % today,
           "DevOps items exist for %d of %d tasks; %d parked; %d customer ask%s unsent; %d stalled over %d days." % (
               k["devops"], k["total"], k["parked"], k["asks_unsent"], "" if k["asks_unsent"] == 1 else "s", k["stalled"], STALLED_DAYS),
           ""]
    if not p["tasks"]:
        out.append("- No open or in-progress task carries `project: %s`." % p["key"])
    for t in p["tasks"]:
        state = "Parked" if t["parked"] else ("In progress" if t["state"] == "in-progress" else "Open")
        if t["parked"]:
            state += " (waiting on %s)" % t["waiting"] if t["waiting"] else " (resumes %s)" % t["resume_on"]
        elif t["due_back"]:
            state += ", due back " + t["resume_on"]
        if t["stalled"]:
            state += ", stalled %d d" % t["progress_age"]
        parts = ["`%s` — DevOps %s. **%s.**" % (t["slug"], ("`%s`" % t["devops"]) if t["devops"] != "none" else "none", state)]
        if t["now"]:
            parts.append("Now (%s): %s" % (t["now_date"], first_sentence(t["now"], 240)))
        elif t["progress_date"]:
            parts.append("Last activity %s; no Progress block." % t["progress_date"])
        if t["next"]:
            parts.append("Next: " + (t["next"][0] if len(t["next"][0]) <= 200 else t["next"][0][:197] + "..."))
        ask = t["customer_ask"] or "none"
        if t["needs"]:
            parts.append("Customer ask (%s): %s" % (ask, t["needs"][0] if len(t["needs"][0]) <= 160 else t["needs"][0][:157] + "..."))
        else:
            parts.append("Customer ask: %s." % ask)
        out.append("- " + " ".join(parts))
    return "\n".join(out) + "\n"


def write_cards(only=None, m=None):
    m = m or build()
    changed = []
    for p in m["projects"]:
        if only and p["key"].lower() != only.lower().replace("\\", "/").strip("/"):
            continue
        path = os.path.join(ROOT, p["key"].replace("/", os.sep), "CONTEXT.md")
        try:
            with open(path, encoding="utf-8", newline="") as f:
                raw = f.read()
        except Exception:
            continue
        nl = "\r\n" if "\r\n" in raw else "\n"
        text = raw.replace("\r\n", "\n")
        hm = SECTION_RE.search(text)
        if not hm:
            continue
        start = hm.end()
        nxt = re.search(r"^## ", text[start:], re.M)
        end = start + nxt.start() if nxt else len(text)
        new = text[:start] + "\n" + render_section(p, m["today"]) + "\n" + text[end:]
        if new != text:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(new.replace("\n", nl))
            changed.append(p["key"])
    return changed


# ---------------------------------------------------------------- cli

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--text", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-cards", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--scope", default="Dev")
    ap.add_argument("--project", default=None)
    a = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    m = build()
    if a.json:
        print(json.dumps(m, indent=1))
    if a.check:
        for p in m["projects"]:
            print("%-46s %-9s card=%-7s standing=%s" % (p["key"], p["status"], p["card"].get("shape"), p["card"].get("standing_date") or "-"))
    if a.write_cards:
        ch = write_cards(a.project, m)
        print("cards regenerated: %s" % (", ".join(ch) if ch else "none (all current)"))
    if a.text or not (a.json or a.check or a.write_cards):
        print(render_text(a.scope, m))


if __name__ == "__main__":
    main()
