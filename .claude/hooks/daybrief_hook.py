#!/usr/bin/env python
"""Day-brief accelerator shared by the SessionStart hook (session_task.py) and the
UserPromptSubmit hook (track_time.py).

The routine it executes is written in AGENTS.md > Continuity loop > Day start: a working day
starts at 05:00 local; the first turn a session takes on a new day begins with the day brief
for where the session sits, and once a day the dashboard is opened as the entry point.

  maybe_brief(session_id, project)  -> prints the brief the first time this session is seen on
                                       the current day key; otherwise prints nothing.
  day_key(now)                       -> the date the working day belongs to (05:00 boundary).

State: .daybrief_state.json next to this file -- {"sessions": {sid: day_key}, "opened": day_key}.
The brief itself comes from ops/bin/daybrief.py (substrate); this file only decides WHEN.
Fail-silent, ASCII-only output, never blocks a turn.
"""
import os, sys, json, datetime, socket, subprocess

DEV_WORKSPACE = os.environ.get("DEV_WORKSPACE", r"C:\Dev")
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".daybrief_state.json")
DAY_STARTS_AT = 5          # local hour; work before 05:00 belongs to the previous day
DASHBOARD_HOST, DASHBOARD_PORT = "127.0.0.1", 8787
DASHBOARD_URL = "http://%s:%d/" % (DASHBOARD_HOST, DASHBOARD_PORT)
KEEP_DAYS = 7


def day_key(now=None):
    now = now or datetime.datetime.now()
    return (now - datetime.timedelta(hours=DAY_STARTS_AT)).date().isoformat()


def _load():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            d = json.load(f)
        return {"sessions": d.get("sessions") or {}, "opened": d.get("opened") or ""}
    except Exception:
        return {"sessions": {}, "opened": ""}


def _save(st):
    cutoff = (datetime.date.today() - datetime.timedelta(days=KEEP_DAYS)).isoformat()
    st["sessions"] = {k: v for k, v in st["sessions"].items() if v >= cutoff}
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(st, f)
    except Exception:
        pass


def _say(text):
    try:
        sys.stdout.write(text.encode("ascii", "replace").decode("ascii") + "\n")
        sys.stdout.flush()
    except Exception:
        pass


def _brief(project):
    sys.path.insert(0, os.path.join(DEV_WORKSPACE, "ops", "bin"))
    import daybrief
    return daybrief.render_text(project)


def _dashboard_up():
    try:
        s = socket.create_connection((DASHBOARD_HOST, DASHBOARD_PORT), timeout=0.3)
        s.close()
        return True
    except Exception:
        return False


def _open_dashboard():
    """Start the dashboard if nothing listens on its port, then open the browser. Once a day."""
    started = False
    if not _dashboard_up():
        try:
            flags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            subprocess.Popen([sys.executable, os.path.join(DEV_WORKSPACE, "ops", "dashboard.py"), "--no-open"],
                             cwd=DEV_WORKSPACE, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, close_fds=True, creationflags=flags)
            started = True
            for _ in range(20):                       # up to ~2 s for the port
                if _dashboard_up():
                    break
                import time; time.sleep(0.1)
        except Exception:
            pass
    try:
        import webbrowser
        webbrowser.open(DASHBOARD_URL)
    except Exception:
        pass
    return started


def maybe_brief(session_id, project, force=False):
    """Print the day brief if this session has not had one on today's day key. `project` is
    the scope as track_time.project_from_cwd resolves it (Dev | customers/C | customers/C/P |
    own/P); None means outside the workspace -> nothing."""
    if project is None:
        return False
    key = day_key()
    st = _load()
    if not force and st["sessions"].get(str(session_id)) == key:
        return False
    try:
        text = _brief(project)
    except Exception as e:  # the brief is an accelerator; a failure must not cost the turn
        text = "[Day brief] unavailable (%s). By hand: python C:\\Dev\\ops\\bin\\daybrief.py --text --scope %s" % (
            e.__class__.__name__, project)
    _say(text)
    st["sessions"][str(session_id)] = key
    if st["opened"] != key:
        started = _open_dashboard()
        st["opened"] = key
        _say("[Day] Dashboard %s: %s (first session of the day; once a day)" % (
            "started and opened" if started else "opened", DASHBOARD_URL))
    _save(st)
    return True


if __name__ == "__main__":
    # manual test: python daybrief_hook.py <session_id> <project> [--force]
    sid = sys.argv[1] if len(sys.argv) > 1 else "manual"
    proj = sys.argv[2] if len(sys.argv) > 2 else "Dev"
    maybe_brief(sid, proj, force="--force" in sys.argv)
