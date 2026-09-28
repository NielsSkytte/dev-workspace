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

Applied by dashboard.line_rows only to measurement on `From` that has no line of its own
that date, spread over the `To` lines named in `Tasks` (every `To` line when `-`) in
proportion to their registered hours. Hours are conserved.

Pure stdlib, ASCII-only.
"""
import io
import os
import re

__all__ = ["path_for", "entries", "for_date"]

ROOT = os.environ.get("TIME_ROOT", r"C:\Dev\ops\time")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


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
