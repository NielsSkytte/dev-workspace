#!/usr/bin/env python
"""Time-tracking hook: emit one heartbeat per turn into ops/time/heartbeats/<utc-date>.jsonl.

Two events, one script (branch on hook_event_name):
  UserPromptSubmit -> stamp this session's turn start (+ cwd + active task) into a state file.
  Stop             -> write the heartbeat {ts_start, ts_end, project, session, task}.

Schema + rollup algorithm live in ops/time/README.md (this is a non-load-bearing accelerator).
Robust by design: reads hook JSON from stdin, always exits 0, never blocks a turn.
ASCII-only (Windows PowerShell 5.1 convention).
"""
import sys, os, json, datetime

TIME_ROOT = os.environ.get("TIME_ROOT", r"C:\Dev\ops\time")
DEV_WORKSPACE = os.environ.get("DEV_WORKSPACE", r"C:\Dev")
HEARTBEATS = os.path.join(TIME_ROOT, "heartbeats")
ACTIVE_TASK = os.path.join(TIME_ROOT, "active-task")
TASKS_ROOT = os.path.join(DEV_WORKSPACE, "ops", "tasks")
STATE_FILE = os.environ.get(
    "TIME_STATE_FILE",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".track_time_state.json"),
)


def project_from_cwd(cwd):
    """Session working dir -> project key. Mirrors capture_turn.scope_from_cwd, but returns the
    bare project path (no 'project:' prefix) and 'Dev' for anything outside customers/ and own/."""
    c = (cwd or "").replace("\\", "/")
    low = c.lower()
    for bucket in ("/customers/", "/own/"):
        i = low.find(bucket)
        if i != -1:
            rest = c[i + 1:].split("/")
            if rest[0].lower() == "customers" and len(rest) >= 3:
                return "customers/%s/%s" % (rest[1], rest[2])
            if rest[0].lower() == "own" and len(rest) >= 2:
                return "own/%s" % rest[1]
    return "Dev"


def read_active_task():
    try:
        with open(ACTIVE_TASK, encoding="utf-8") as f:
            slug = f.read().strip()
            return slug or None
    except Exception:
        return None


def task_project(slug):
    """The `project:` frontmatter field of a task file, or None if not found."""
    if not slug:
        return None
    for statedir in ("open", "in-progress", "done", "cancelled"):
        try:
            with open(os.path.join(TASKS_ROOT, statedir, slug + ".md"), encoding="utf-8") as f:
                for line in f:
                    low = line.strip().lower()
                    if low.startswith("project:"):
                        val = line.split(":", 1)[1].strip().split("#", 1)[0].strip()
                        return val or None
        except Exception:
            continue
    return None


def active_task_for(project):
    """The active task, but only if it belongs to `project` -- a stale or foreign task tag
    (left over from another project's session) must never bill to this one."""
    slug = read_active_task()
    if slug and task_project(slug) == project:
        return slug
    return None


def load_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(state):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f)
    except Exception:
        pass


def now_z():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    raw = sys.stdin.read()
    try:
        hook = json.loads(raw)
    except Exception:
        hook = {}
    if hook.get("stop_hook_active"):
        return  # avoid loops
    event = hook.get("hook_event_name", "")
    sid = str(hook.get("session_id", "unknown"))
    cwd = hook.get("cwd", "")
    state = load_state()

    if event == "UserPromptSubmit":
        # Stamp the turn's start; remember cwd + the task active at submit time
        # (only if that task belongs to this session's project).
        state[sid] = {"start": now_z(), "cwd": cwd,
                      "task": active_task_for(project_from_cwd(cwd))}
        save_state(state)
        return

    # Stop (or anything else): write the heartbeat for this turn.
    s = state.get(sid) or {}
    ts_start = s.get("start") or now_z()           # fall back to a point if no submit was seen
    ts_end = now_z()
    project = project_from_cwd(s.get("cwd") or cwd)
    task = s.get("task")

    rec = {"ts_start": ts_start, "ts_end": ts_end,
           "project": project, "session": sid[:8], "task": task}
    try:
        os.makedirs(HEARTBEATS, exist_ok=True)
        date = ts_end[:10]  # UTC date for the file name
        with open(os.path.join(HEARTBEATS, date + ".jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
