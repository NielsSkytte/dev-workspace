#!/usr/bin/env python
"""SessionStart hook: establish the session's active task for a customer project.

Why this exists: the project walk in CLAUDE.md *instructs* the assistant to ask which
task a session bills to. Instructions get skipped. This hook is deterministic -- when
the answer is unambiguous it writes the marker itself, and only asks when there is a
real choice.

Behaviour, by what the session's cwd resolves to:
  customer project / customer node, exactly one open task -> SET it, announce it
  ... several open tasks                                  -> emit the list; first reply asks
  ... no open tasks                                       -> offer: create one, or project level
  Dev / own/                                              -> no task level; nudge only
  outside the workspace                                   -> silent

Every workspace session also gets the **unfinalized-days nudge**: days with tracked time
whose /log never ran. Sessions left open for days cost nothing (the 15+5 model discards
idle gaps) and `rollup.py` catches missed days up in bulk, so this is a reminder, not a
repair.

The marker entry written here is keyed by THIS session id and never touches another
session's -- concurrent sessions on different projects are the normal case.

Schema + rules live in ops/time/README.md (non-load-bearing accelerator).
Robust by design: reads hook JSON from stdin, always exits 0, never blocks a session.
ASCII-only (Windows PowerShell 5.1 convention).
"""
import sys, os, json, glob, datetime

TIME_ROOT = os.environ.get("TIME_ROOT", r"C:\Dev\ops\time")
DEV_WORKSPACE = os.environ.get("DEV_WORKSPACE", r"C:\Dev")
ACTIVE_TASK = os.path.join(TIME_ROOT, "active-task")
TASKS_ROOT = os.path.join(DEV_WORKSPACE, "ops", "tasks")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from track_time import project_from_cwd, customer_of, set_session_task
except Exception:
    sys.exit(0)

HEARTBEATS = os.path.join(TIME_ROOT, "heartbeats")
TIMESHEET = os.path.join(TIME_ROOT, "timesheet")


def say(text):
    """Print ASCII-safe. Task titles carry non-cp1252 characters (arrows, em dashes) and a
    Windows console encode error would be swallowed by the top-level guard -- silently
    turning this hook off for precisely the projects with the most tasks."""
    try:
        sys.stdout.write(text.encode("ascii", "replace").decode("ascii") + "\n")
    except Exception:
        pass


def field(path, name):
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip().lower().startswith(name + ":"):
                    return line.split(":", 1)[1].split("#", 1)[0].strip()
    except Exception:
        pass
    return ""


def open_tasks_for(project):
    """Open/in-progress tasks whose project: is `project`, or -- when the session sits at a
    customer node -- any task on one of that customer's projects."""
    cust = customer_of(project)
    out = []
    for state in ("in-progress", "open"):
        for path in sorted(glob.glob(os.path.join(TASKS_ROOT, state, "*.md"))):
            tproj = field(path, "project")
            if not tproj:
                continue
            hit = (tproj == project) or (cust and customer_of(tproj) == cust)
            if hit:
                out.append({"slug": os.path.basename(path)[:-3], "state": state,
                            "project": tproj, "title": field(path, "title")})
    return out


def unfinalized_days():
    """Complete past days that have heartbeats but no timesheet -- i.e. days whose /log
    never ran. `rollup.py` catches them up whenever /log next runs, so this is a nudge,
    not a repair. Heartbeat files are named by UTC date and timesheets by local date, so
    a day either side of the boundary can read a few hours off; it is advisory only."""
    try:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        hb = {os.path.basename(p)[:10] for p in glob.glob(os.path.join(HEARTBEATS, "*.jsonl"))}
        ts = {os.path.basename(p)[:10] for p in glob.glob(os.path.join(TIMESHEET, "*", "*.md"))}
        return sorted(d for d in hb - ts if d < today)
    except Exception:
        return []


def nudge():
    """Surface days whose /log never ran. Fires for EVERY workspace session, including
    Dev and own/ -- forgetting to wrap up is not a customer-project-only habit."""
    days = unfinalized_days()
    if not days:
        return
    shown = ", ".join(days[:5]) + (" +%d more" % (len(days) - 5) if len(days) > 5 else "")
    say("[Time] %d day(s) with tracked time but no finalized timesheet: %s. Mention this "
        "in the first reply and offer /log -- it finalizes every missed day at once "
        "(catch-up), distills memory, and backs up. Nothing is lost meanwhile; the hours "
        "are already captured." % (len(days), shown))


def main():
    try:
        hook = json.loads(sys.stdin.read())
    except Exception:
        hook = {}
    project = project_from_cwd(hook.get("cwd", ""))
    if project is None:
        return  # outside the workspace

    nudge()

    if not customer_of(project):
        return  # Dev or own/ -- no task level there

    # NOTE: this session gets its OWN marker entry. It must never clear another
    # session's -- concurrent sessions on different projects are normal here, and a
    # shared single record made each new session wipe the previous one's tag.
    tasks = open_tasks_for(project)

    if len(tasks) == 1:
        t = tasks[0]
        set_session_task(hook.get("session_id", "unknown"), t["slug"])
        say("[Time] Active task set automatically (the only open task on this project): "
              "%s -- %s\nTime this session bills to %s / %s. Say so in your first reply; "
              "use /switch-task to change it."
              % (t["slug"], t["title"] or "(no title)", t["project"], t["slug"]))
        return

    if len(tasks) > 1:
        lines = ["[Time] %d open tasks for %s -- ASK which one this session bills to "
                 "before the first request, then set it with /switch-task:" % (len(tasks), project)]
        for t in tasks:
            lines.append("  - %s [%s] %s -- %s" % (t["slug"], t["state"], t["project"],
                                                   t["title"] or "(no title)"))
        lines.append("  - or none: time bills to the project, no Activity/Task dimension")
        say("\n".join(lines))
        return

    say("[Time] No open tasks for %s. In the first reply ask whether to (a) create one "
          "with /task -- right when the work is a user story you would raise as an Azure "
          "DevOps work item, or (b) track at project level, which is a valid F&O line and "
          "the correct answer for work that is not story-shaped. Do not push (a)." % project)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
