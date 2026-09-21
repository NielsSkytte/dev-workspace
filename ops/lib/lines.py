"""Line descriptions: what a day's work on one F&O line actually was.

A timesheet row reads `customers/Carl-Ras/datahub | 230-02 | - | - | 3.00 | yes` and says
nothing about the work. That is a problem twice over: an untagged line cannot be placed on
a task without opening the transcript, and an entry figure above the measured hours has
nothing beside it to justify it.

The sentence itself is written by a session at `/log` (`ops/bin/linedesc.py` prepares the
material), because a local model was tried for this in July and August and was switched off
on 2026-09-02 for writing summaries that contradicted their turn -- see the memory record
`local-summarizer-off`. It lands in `ops/time/lines/<YYYY-MM>/<date>.md`, a table with the
same key as the timesheet day beside it.

**Regenerable, so Guardrail 7 holds**: delete the file and nothing is lost that
`ops/memory/daily/<date>.md` does not still hold -- it is a written-down reading of the
transcript, not a second source for it.

Read-only. Pure stdlib, ASCII-only.
"""
import os
import re

__all__ = ["ROOT", "dir_for", "path_for", "dimkey", "read_day", "read_month", "render",
           "HEADER"]

ROOT = os.environ.get("TIME_ROOT", r"C:\Dev\ops\time")

HEADER = """# Line descriptions - %(date)s (%(dow)s)

What each F&O line on this date was, in a sentence someone outside the session can read.
Written at /log from ops/memory/daily/%(date)s.md; the key is the timesheet's own
(project + activity + task), so a line here answers the line beside it in
timesheet/%(month)s/%(date)s.md.

Regenerable -- `python ops/bin/linedesc.py %(date)s` prints the material again.

"""

COLUMNS = "| Project | Activity | Task | Hours | Description |"
RULE = "|---|---|---|---|---|"


def dir_for(date, root=None):
    return os.path.join(root or ROOT, "lines", date[:7])


def path_for(date, root=None):
    return os.path.join(dir_for(date, root), date + ".md")


def dimkey(project, activity, fno_task):
    """The key a description is filed under: the F&O dimension, minus the date.

    Identical to the timesheet row's identity, so the two files line up row for row. A
    placeholder (`-`, `none`) is the absence of a value on both sides."""
    def one(v):
        v = (v or "").strip()
        return "" if v in ("-", "") or v.lower() == "none" else v
    return "%s|%s|%s" % (project.strip(), one(activity), one(fno_task))


def read_day(date, root=None):
    """-> {dimkey: description}. Missing file or unreadable table gives {}.

    Tolerant on purpose: this is written by hand (by a session) and a malformed row should
    cost that row, not the day."""
    path = path_for(date, root)
    out = {}
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except Exception:
        return out
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) != 5 or cells[0] == "Project" or set(cells[0]) <= set("-"):
            continue
        desc = cells[4].strip()
        if desc and desc != "-":
            out[dimkey(cells[0], cells[1], cells[2])] = desc
    return out


def read_month(month, root=None):
    """-> {date: {dimkey: description}} for every day of `YYYY-MM` that has a file."""
    import glob
    out = {}
    for p in sorted(glob.glob(os.path.join(root or ROOT, "lines", month, "*.md"))):
        date = os.path.basename(p)[:-3]
        if re.match(r"^\d{4}-\d{2}-\d{2}$", date):
            out[date] = read_day(date, root)
    return out


def render(date, rows):
    """The whole file for one date. `rows` is [{project, activity, fno_task, hours,
    description}] in the order the timesheet has them."""
    import datetime
    dow = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%a")
    body = [HEADER % {"date": date, "dow": dow, "month": date[:7]}, COLUMNS, RULE]
    for r in rows:
        body.append("| %s | %s | %s | %.2f | %s |" % (
            r["project"], r.get("activity") or "-", r.get("fno_task") or "-",
            r.get("hours") or 0.0,
            re.sub(r"\s*\|\s*", " / ", (r.get("description") or "").strip()) or "-"))
    return "\n".join(body) + "\n"
