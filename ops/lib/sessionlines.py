"""Which F&O line a work session's time went to.

A timesheet day groups by DIMENSION, not by session: three sessions on one customer
with nothing tagged are one line of 0.75 h. That is right for billing and wrong for
entry -- the three were a Fabric cluster error, a GTM deployment and the Marketo
outbound work, and they belong under three different F&O tasks.

Splitting the line is a correction to the day file (dashboard.timesheet_split), and
the file is authoritative once written. But the EVIDENCE behind a line is rebuilt from
the heartbeats every read, and the heartbeats are immutable -- so without a record of
where each session went, both halves of a split line keep showing all three sessions.
This is that record:

    | Date | Session | Project | Activity | Task | Note | Recorded |

Read by `collect_line_sessions` to key a session's turns under the dimensions it was
split onto, instead of the ones its work-task happens to carry now. Append-only, a
later row for the same session wins, and it holds nothing F&O ever sees -- the hours
live in the timesheet, this only says which line they are evidence for.

Pure stdlib, ASCII-only.
"""
import datetime
import io
import os
import re

__all__ = ["path_for", "entries", "assigned", "record", "HEADER"]

ROOT = os.environ.get("TIME_ROOT", r"C:\Dev\ops\time")

HEADER = """# Session to F&O line

Which timesheet line each work session's time was split onto. Written from the Time
page when one day's line is split between the sessions behind it; read only to show
the right sessions under the right line. Nothing here is billed or entered into F&O.
See ops/time/README.md 6.4.

| Date | Session | Project | Activity | Task | Note | Recorded |
|---|---|---|---|---|---|---|
"""

_ROW = re.compile(r"^\|(.*)\|\s*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SESSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{3,63}$")


def path_for(root=None):
    return os.path.join(root or ROOT, "session-lines.md")


def _clean(v):
    return re.sub(r"\s+", " ", re.sub(r"[|\n\r]+", " ", v or "")).strip()


def entries(root=None):
    """Every row, in file order. Missing file gives []."""
    try:
        with io.open(path_for(root), encoding="utf-8", newline="") as f:
            text = f.read()
    except Exception:
        return []
    out = []
    for line in text.splitlines():
        m = _ROW.match(line.strip())
        if not m:
            continue
        c = [x.strip() for x in m.group(1).split("|")]
        if len(c) < 3 or not DATE_RE.match(c[0]) or not SESSION_RE.match(c[1]) or not c[2]:
            continue
        blank = lambda v: "" if v in ("", "-") else v
        out.append({"date": c[0], "session": c[1], "project": c[2],
                    "activity": blank(c[3] if len(c) > 3 else ""),
                    "fno_task": blank(c[4] if len(c) > 4 else ""),
                    "note": blank(c[5] if len(c) > 5 else ""),
                    "recorded": c[6] if len(c) > 6 else ""})
    return out


def assigned(root=None, rows=None):
    """-> {(date, session, project.lower()): {'activity','fno_task'}}, last row winning.

    A correction is another row rather than an edit, so the file stays append-only and
    reads as the history of the decision."""
    out = {}
    for e in (entries(root) if rows is None else rows):
        out[(e["date"], e["session"], e["project"].lower())] = {
            "activity": e["activity"], "fno_task": e["fno_task"]}
    return out


def record(date, session, project, activity="", fno_task="", note="", root=None):
    """Append one session's destination. -> (ok, message)."""
    date, session = (date or "").strip(), (session or "").strip()
    project = _clean(project)
    if not DATE_RE.match(date):
        return False, "bad date: %r" % (date,)
    if not SESSION_RE.match(session):
        return False, "not a session id: %r" % (session,)
    if not project:
        return False, "no project"
    activity, fno_task = _clean(activity)[:64], _clean(fno_task)[:64]
    note = _clean(note)[:200]
    have = assigned(root).get((date, session, project.lower()))
    if have and have["activity"] == activity and have["fno_task"] == fno_task:
        return True, "%s is already on that line" % session

    path = path_for(root)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        exists = os.path.exists(path)
        with io.open(path, "a" if exists else "w", encoding="utf-8", newline="") as f:
            if not exists:
                f.write(HEADER)
            f.write("| %s | %s | %s | %s | %s | %s | %s |\n"
                    % (date, session, project, activity or "-", fno_task or "-",
                       note or "-", datetime.date.today().isoformat()))
    except Exception as exc:
        return False, str(exc)
    return True, "%s -> %s" % (session, fno_task or activity or "the untagged line")
