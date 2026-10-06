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


def _has_identity(d):
    """A folder is a project when it holds an AGENTS.md (legacy: CLAUDE.md)."""
    return any(os.path.isfile(os.path.join(d, n)) for n in ("AGENTS.md", "CLAUDE.md"))


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
    project only if it has an AGENTS.md (or legacy CLAUDE.md) -- a grandfathered flat code repo under
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
        if len(rest) >= 3 and _has_identity(
                os.path.join(root, rest[0], rest[1], rest[2])):
            return "customers/%s/%s" % (rest[1], rest[2])
        if len(rest) >= 2:
            return "customers/%s" % rest[1]
    if rest and rest[0].lower() == "own" and len(rest) >= 2 and _has_identity(
            os.path.join(root, rest[0], rest[1])):
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


def _attrib(sid, state_entry, project, task):
    """Say it when this turn is about to produce a line that cannot be entered.

    `resolve()` already decided the project and whether a task tag survived; the three
    ways it drops one -- no task held, the held task on another customer, a turn on a
    customer node -- each produce an F&O line short of something the customer requires,
    and none of them said anything. The work then gets done, the day gets finalized, and
    it surfaces at the month close as a line with no Task.

    The judgement is `ops/lib/attribution.drift`, which resolves the dimensions through
    the same call the entry page makes, so the two cannot disagree about whether a line is
    enterable.

    Reported ONCE per session per kind per project. A per-turn warning is a warning nobody
    reads. Fail-silent and ASCII-only, like everything else in this hook: a check that can
    break time tracking is worse than no check."""
    try:
        if not project or not project.startswith("customers/"):
            return                                  # Dev and own/ are never entered
        sys.path.insert(0, os.path.join(DEV_WORKSPACE, "ops"))
        from lib import attribution

        m = load_marker()
        held = ((m.get("sessions") or {}).get(sid) or {}).get("slug") or ""
        d = attribution.drift(project, task, held, task_project(held) if held else "",
                              root=DEV_WORKSPACE)
        if not d:
            return
        seen = state_entry.setdefault("warned", [])
        key = d["kind"] + ":" + d["project"]
        if key in seen:
            return
        seen.append(key)
        print("[time] %s\n       %s" % (d["why"].encode("ascii", "replace").decode("ascii"),
                                        d["fix"].encode("ascii", "replace").decode("ascii")))
    except Exception:
        pass


def _daybrief(sid, project):
    """Day brief on the first turn of a new day -- AGENTS.md > Continuity loop > Day start.
    The decision (05:00 boundary, once per session per day, dashboard once a day) lives in
    daybrief_hook.py; the brief itself is ops/bin/daybrief.py. Fail-silent."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from daybrief_hook import maybe_brief
        maybe_brief(sid, project)
    except Exception:
        pass


IDLE_TIMEOUT_MIN = 15   # matches ops/time/README.md section 3 -- one rule, both levels

# Tools that block on the USER. The turn stays open while one is pending, so its wait is
# not work. Registered as PreToolUse/PostToolUse matchers, so the hook fires once per
# question rather than once per tool call.
BLOCKING_TOOLS = ("AskUserQuestion",)


def _mins_between(a, b):
    """Minutes from timestamp a to b, or None if either is unparseable."""
    try:
        fmt = "%Y-%m-%dT%H:%M:%SZ"
        return (datetime.datetime.strptime(b, fmt)
                - datetime.datetime.strptime(a, fmt)).total_seconds() / 60.0
    except Exception:
        return None


def subtract_waits(ts_start, ts_end, waits):
    """[ts_start, ts_end] minus each [a, b] in waits -> the active segments.

    A turn that asks the user a question stays OPEN until they answer, so its single
    heartbeat covers the wait. Found 2026-08-20, session 45041831: an AskUserQuestion
    issued at 09:15:55 was answered at 14:25:44 and the turn's heartbeat spanned 325
    min, 310 of which was the question sitting there. Cutting the wait out leaves the
    two real windows -- which is exactly how that day was reconstructed by hand."""
    segs = [(ts_start, ts_end)]
    for a, b in waits:
        nxt = []
        for s, e in segs:
            if b <= s or a >= e:          # no overlap
                nxt.append((s, e))
                continue
            if a > s:
                nxt.append((s, a))
            if b < e:
                nxt.append((b, e))
        segs = nxt
    return [(s, e) for s, e in segs if e > s]


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
        prev = state.get(sid) or {}
        state[sid] = {"start": now_z(), "cwd": cwd,
                      "project": project, "task": task,
                      "last_stop": None, "waits": [],
                      # what has already been said to this session, so a drift is
                      # reported once and not on every turn that repeats it
                      "warned": prev.get("warned") or []}
        _attrib(sid, state[sid], project, task)
        save_state(state)
        _daybrief(sid, project)   # prints only on the first turn of a new day
        return

    # PreToolUse/PostToolUse are registered for BLOCKING_TOOLS only, so this costs one
    # process per question asked, not one per tool call.
    if event in ("PreToolUse", "PostToolUse"):
        if hook.get("tool_name") not in BLOCKING_TOOLS:
            return
        s = state.get(sid)
        if not s:
            return  # no turn in flight for this session -- nothing to attribute a wait to
        if event == "PreToolUse":
            s["ask_at"] = now_z()
        else:
            asked = s.pop("ask_at", None)
            end = now_z()
            gap = _mins_between(asked, end) if asked else None
            # Only a wait past the idle timeout is deducted. Answering in twenty seconds
            # is ordinary turn time, and fragmenting the heartbeat over it would add a
            # tail buffer and a 0.5 h floor for nothing.
            if gap is not None and gap > IDLE_TIMEOUT_MIN:
                s.setdefault("waits", []).append([asked, end])
        state[sid] = s
        save_state(state)
        return

    # Stop (or anything else): write the heartbeat for this turn.
    s = state.get(sid) or {}
    ts_end = now_z()
    ts_start = s.get("start") or ts_end            # fall back to a point if no submit was seen

    # A Stop can fire WITHOUT a preceding UserPromptSubmit -- a `!`-prefixed bash-input does
    # exactly this. The stamped start then belongs to some earlier turn, and reusing it invents
    # every idle minute since. Verified 2026-08-03, session 5bbffdc6: the real turn ended at
    # 10:24:39 and wrote its own correct heartbeat; a bash-input at 16:03 re-Stopped the session
    # and wrote a SECOND heartbeat with the same ts_start, spanning 339.8 min, of which the
    # transcript shows zero activity after 10:27:57. It put 5.5 phantom hours on a customer line.
    #
    # A later Stop is only trusted to extend the turn if it lands within the idle timeout of the
    # previous one -- that is the legitimate case (a turn yields on background work, then
    # continues). Beyond it the gap was idle by the same rule the rollup applies between turns,
    # so the heartbeat becomes a point at ts_end and the idle time is discarded, not billed.
    last = s.get("last_stop")
    if last:
        gap = _mins_between(last, ts_end)
        if gap is None or gap > IDLE_TIMEOUT_MIN:
            ts_start = ts_end
    if s:
        s["last_stop"] = ts_end
        state[sid] = s
        save_state(state)
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
    # A turn that waited on the user is written as its ACTIVE segments, not as one span.
    segments = subtract_waits(ts_start, ts_end, s.get("waits") or [])
    if not segments:
        return  # the whole turn was a wait -- nothing worked, nothing to record
    try:
        os.makedirs(HEARTBEATS, exist_ok=True)
        date = ts_end[:10]  # UTC date for the file name
        with open(os.path.join(HEARTBEATS, date + ".jsonl"), "a", encoding="utf-8") as f:
            for seg_start, seg_end in segments:
                f.write(json.dumps({"ts_start": seg_start, "ts_end": seg_end,
                                    "project": project, "session": sid[:8],
                                    "task": task}) + "\n")
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
