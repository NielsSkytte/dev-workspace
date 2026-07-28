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


MARKER_TTL_DAYS = 7


def load_marker():
    """-> {"sessions": {sid: {slug, set_at}}, "unclaimed": {slug, set_at} | None}

    The marker is PER SESSION (corrected 2026-07-28, same day as ADR-003): several
    sessions run concurrently on different projects, and a single shared record meant
    each new session wiped the previous one's tag. Each session owns its own entry.

    Three formats are accepted, so nothing written by an older build or by hand is lost:
      map        {"sessions": {...}, "unclaimed": {...}}   -- current
      single     {"slug", "session", "set_at"}             -- ADR-003 first cut
      bare slug  one line of text                          -- original / by hand
    The latter two carry no session, so they land in `unclaimed`."""
    try:
        with open(ACTIVE_TASK, encoding="utf-8") as f:
            raw = f.read().strip()
    except Exception:
        return {"sessions": {}, "unclaimed": None}
    if not raw:
        return {"sessions": {}, "unclaimed": None}
    if raw.startswith("{"):
        try:
            d = json.loads(raw)
        except Exception:
            return {"sessions": {}, "unclaimed": None}
        if "sessions" in d or "unclaimed" in d:
            return {"sessions": d.get("sessions") or {},
                    "unclaimed": d.get("unclaimed") or None}
        slug, sid = d.get("slug"), d.get("session")
        if not slug:
            return {"sessions": {}, "unclaimed": None}
        if sid:
            return {"sessions": {sid: {"slug": slug, "set_at": d.get("set_at") or now_z()}},
                    "unclaimed": None}
        return {"sessions": {}, "unclaimed": {"slug": slug, "set_at": d.get("set_at") or now_z()}}
    return {"sessions": {},
            "unclaimed": {"slug": raw.splitlines()[0].strip(), "set_at": now_z()}}


def save_marker(m):
    """Write the marker, dropping session entries older than MARKER_TTL_DAYS so the map
    cannot grow without bound across months of sessions."""
    cutoff = (datetime.datetime.now(datetime.timezone.utc)
              - datetime.timedelta(days=MARKER_TTL_DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    m["sessions"] = {k: v for k, v in (m.get("sessions") or {}).items()
                     if (v or {}).get("set_at", "") >= cutoff}
    try:
        os.makedirs(os.path.dirname(ACTIVE_TASK), exist_ok=True)
        with open(ACTIVE_TASK, "w", encoding="utf-8") as f:
            json.dump(m, f)
    except Exception:
        pass


def set_session_task(sid, slug):
    m = load_marker()
    m.setdefault("sessions", {})[sid] = {"slug": slug, "set_at": now_z()}
    save_marker(m)


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


def customer_of(project):
    """'customers/<Client>[/<Project>]' -> '<client>' (lowercased); None for Dev / own/."""
    if not project:
        return None
    parts = project.split("/")
    if len(parts) >= 2 and parts[0].lower() == "customers":
        return parts[1].lower()
    return None


def resolve(cwd, sid):
    """-> (project, task_slug) for this turn.

    The active task DECIDES the project, cwd is the fallback (reversed 2026-07-28,
    ADR-003) -- one project routinely spans several repos and one repo hosts several
    tasks, so the folder cannot express which work is in play.

    Guard: the task may only override cwd WITHIN THE SAME CUSTOMER. A customer node
    (customers/<Client>) is overridden by a task on one of its projects, which is how
    node-level UNSET time resolves itself. Dev and own/ are NEVER overridden -- moving
    workspace time onto a customer is the direction that over-bills, and it stays a
    deliberate call at the review gate.

    Staleness: only THIS session's own marker entry is read, so a task set in another
    session -- past or concurrent -- can never tag this one."""
    cwd_proj = project_from_cwd(cwd)
    if cwd_proj is None:
        return None, None

    m = load_marker()
    slug = ((m.get("sessions") or {}).get(sid) or {}).get("slug")
    if not slug:
        # Nothing of ours. A slash command cannot know the session id, so it leaves an
        # UNCLAIMED entry -- adopt it only if it passes the same-customer test below,
        # which stops a concurrent session on another customer from stealing it.
        pending = (m.get("unclaimed") or {}).get("slug")
        if not pending:
            return cwd_proj, None
        if not _fits(pending, cwd_proj):
            return cwd_proj, None
        m["sessions"] = m.get("sessions") or {}
        m["sessions"][sid] = {"slug": pending, "set_at": now_z()}
        m["unclaimed"] = None
        save_marker(m)
        slug = pending

    tproj = task_project(slug)
    if not tproj:
        return cwd_proj, None
    if tproj == cwd_proj:
        return cwd_proj, slug
    cust = customer_of(cwd_proj)
    if cust and cust == customer_of(tproj):
        return tproj, slug                # same customer -> the task names the real project
    return cwd_proj, None                 # cross-customer, or Dev/own -> cwd wins, no tag


def _fits(slug, cwd_proj):
    """Would this task legitimately apply to a session rooted at cwd_proj?"""
    tproj = task_project(slug)
    if not tproj:
        return False
    if tproj == cwd_proj:
        return True
    cust = customer_of(cwd_proj)
    return bool(cust and cust == customer_of(tproj))


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
        # Stamp the turn's start; resolve project + task as of submit time.
        project, task = resolve(cwd, sid)
        if project is None:
            return  # outside the workspace -> not tracked
        state[sid] = {"start": now_z(), "cwd": cwd,
                      "project": project, "task": task}
        save_state(state)
        return

    # Stop (or anything else): write the heartbeat for this turn.
    s = state.get(sid) or {}
    ts_start = s.get("start") or now_z()           # fall back to a point if no submit was seen
    ts_end = now_z()
    project = s.get("project")
    task = s.get("task")
    if project is None:                            # no submit seen this session -- resolve now
        project, task = resolve(s.get("cwd") or cwd, sid)
    if project is None:
        return  # outside the workspace -> not tracked

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
