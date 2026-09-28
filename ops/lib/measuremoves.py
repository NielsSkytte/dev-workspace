"""Measurement that follows a timesheet line moved to another project.

A day's measurement is rebuilt from the heartbeats on every read, and the heartbeats are
immutable: work done in a session rooted in `own/MetaAtomic` is measured on
`own/MetaAtomic`, whatever the timesheet says afterwards. When /log moves that line to a
customer project, the hours move and the measurement stays behind, on a project with no
line that day. The Time page then shows the customer line with next to no measured time
and no value, and its F&O entry falls to work time.

Moving it cannot be inferred -- work on one project is not evidence for another -- so the
decision is written down here, the same kind of register as `not-invoiced.md`:

    | Date       | From           | To                          | Tasks                        | Note | Recorded   |
    |------------|----------------|-----------------------------|------------------------------|------|------------|
    | 2026-09-09 | own/MetaAtomic | customers/Carl-Ras/datahub  | CarlRData-666, CarlRData-555 | ...  | 2026-09-28 |

Written by dashboard.reassign whenever a line changes project, and by hand for a move made
in the timesheet file directly. Applied by dashboard.line_rows only to measurement on
`From` that has no line of its own that date, spread over the `To` lines named in `Tasks`
(every `To` line when `-`) in proportion to their registered hours. Hours are conserved.

Pure stdlib, ASCII-only.
"""
import datetime
import io
import os
import re

__all__ = ["path_for", "entries", "for_date", "record", "HEADER"]

ROOT = os.environ.get("TIME_ROOT", r"C:\Dev\ops\time")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

HEADER = """# Measurement moves

Where a timesheet line was moved to another project at /log, the measurement follows it.
The heartbeats stay on the project the session ran in; this register says where that
day's measurement belongs instead. Read by the Time page (dashboard.line_rows via
lib/measuremoves.py); written by the page's reassign and by hand. Applied only to
measurement on `From` that has no line of its own that date, spread over the `To` lines
named in `Tasks` (`-` = every `To` line) by their registered hours. Nothing here changes
billed hours.

| Date | From | To | Tasks | Note | Recorded |
|---|---|---|---|---|---|
"""


def path_for(root=None):
    return os.path.join(root or ROOT, "measure-moves.md")


def entries(root=None):
    """Every row -> [{date, from, to, tasks[]}]. Missing file gives []."""
    try:
        with io.open(path_for(root), encoding="utf-8", newline="") as f:
            text = f.read()
    except Exception:
        return []
    out = []
    for line in text.splitlines():
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) < 3 or not DATE_RE.match(c[0]) or not c[1] or not c[2]:
            continue
        tasks = c[3] if len(c) > 3 else ""
        out.append({"date": c[0], "from": c[1], "to": c[2],
                    "tasks": [] if tasks in ("", "-")
                    else [t.strip() for t in tasks.split(",") if t.strip()]})
    return out


def for_date(date, rows=None, root=None):
    return [e for e in (entries(root) if rows is None else rows) if e["date"] == date]


def _clean(v):
    return re.sub(r"\s+", " ", re.sub(r"[|\n\r]+", " ", v or "")).strip()


def record(date, from_project, to_project, tasks=(), note="", root=None):
    """Append one move. -> (ok, message). A row already saying the same is not repeated."""
    date = (date or "").strip()
    src, dst = _clean(from_project), _clean(to_project)
    if not DATE_RE.match(date):
        return False, "bad date: %r" % (date,)
    if not src or not dst or src == dst:
        return False, "a move needs two different projects"
    tasks = [_clean(t) for t in tasks if _clean(t)]
    for e in entries(root):
        if (e["date"], e["from"], e["to"], e["tasks"]) == (date, src, dst, tasks):
            return True, "already recorded"
    path = path_for(root)
    try:
        exists = os.path.exists(path)
        with io.open(path, "a" if exists else "w", encoding="utf-8", newline="") as f:
            if not exists:
                f.write(HEADER)
            f.write("| %s | %s | %s | %s | %s | %s |\n"
                    % (date, src, dst, ", ".join(tasks) or "-", _clean(note)[:200] or "-",
                       datetime.date.today().isoformat()))
    except Exception as exc:
        return False, str(exc)
    return True, "measurement on %s follows to %s" % (src, dst)
