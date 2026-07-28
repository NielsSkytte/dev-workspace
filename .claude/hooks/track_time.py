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
    """Session working dir -> project key, anchored at the workspace root.
    Mirrors capture_turn.scope_from_cwd. Any depth below a project rolls up to
    the project (customers/<client>/<project> or own/<project>); a customer
    node (customers/<client>, above projects) is its own key; anything else
    under the workspace is 'Dev'. Returns None for a cwd OUTSIDE the
    workspace -- the hooks are registered machine-wide in the user-level
    settings, and non-workspace sessions must not be tracked.
    realpath canonicalizes casing and resolves junctions/subst drives so one
    project never splits into case-variant keys. A depth-3 folder counts as a
    project only if it has a CLAUDE.md -- a grandfathered flat code repo under
    a customer (e.g. Tystofte/PowerPortal.wiki) bills to the customer, and a
    non-project folder under own/ bills to Dev."""
    if not cwd:
        return None
    root = os.path.realpath(DEV_WORKSPACE)
    c = os.path.realpath(cwd)
    if os.path.normcase(c) == os.path.normcase(root):
        return "Dev"
    if not os.path.normcase(c).startswith(os.path.normcase(root) + os.sep):
        return None
    rest = [seg for seg in c[len(root) + 1:].split(os.sep) if seg]
    if rest and rest[0].lower() == "customers":
        if len(rest) >= 3 and os.path.isfile(
                os.path.join(root, rest[0], rest[1], rest[2], "CLAUDE.md")):
            return "customers/%s/%s" % (rest[1], rest[2])
        if len(rest) >= 2:
            return "customers/%s" % rest[1]
    if rest and rest[0].lower() == "own" and len(rest) >= 2 and os.path.isfile(
            os.path.join(root, rest[0], rest[1], "CLAUDE.md")):
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
        project = project_from_cwd(cwd)
        if project is None:
            return  # outside the workspace -> not tracked
        state[sid] = {"start": now_z(), "cwd": cwd,
                      "task": active_task_for(project)}
        save_state(state)
        return

    # Stop (or anything else): write the heartbeat for this turn.
    s = state.get(sid) or {}
    ts_start = s.get("start") or now_z()           # fall back to a point if no submit was seen
    ts_end = now_z()
    project = project_from_cwd(s.get("cwd") or cwd)
    if project is None:
        return  # outside the workspace -> not tracked
    task = s.get("task")

    # Every Stop writes -- a turn can Stop several times (yield on background
    # work, then continue), and each later Stop extends the tracked interval.
    # Duplicates are free: the rollup merges overlapping intervals, and Claude
    # Code deduplicates the identical command strings of the workspace +
    # user-level registrations anyway.
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
