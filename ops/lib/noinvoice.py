"""Lines that must never go on a customer invoice.

Some work happens inside a customer folder and is not that customer's to pay for:
registering the time itself, fixing the setup, building the dashboard. The folder says
`customers/<Client>/<project>` and the rollup therefore marks it billable, because that is
the only rule it has.

`ops/time/not-invoiced.md` is the decision, written down. It is a **register**, not a
derived view -- the same kind of file as `absence.md`, which also records something only
the owner can know and which the rollup then applies. Deleting it loses the decisions, so
it is the one thing here that is not regenerable (Guardrail 7 allows a register; what it
forbids is a second copy of something already derivable).

**The register wins.** A line it covers is never billable, whatever the timesheet file,
the folder or a later correction says. That is what makes "do not invoice this under any
circumstances" mean it: the mark survives a re-derivation, a hand edit and a reassignment,
and it can be set on a day that is still running, before the day file exists at all.

    | Date       | Project                     | Activity | Task | Why              | Recorded   |
    |------------|-----------------------------|----------|------|------------------|------------|
    | 2026-09-21 | customers/Carl-Ras/datahub  | -        | -    | registering time | 2026-09-21 |

A row matches by date and project. `Activity` and `Task` narrow it when given; `-` means
"any". `*` in Date means every date for that project -- for work that is never billable
wherever it turns up.

Pure stdlib, ASCII-only.
"""
import datetime
import io
import os
import re

__all__ = ["path_for", "entries", "covers", "record", "HEADER"]

ROOT = os.environ.get("TIME_ROOT", r"C:\Dev\ops\time")

HEADER = """# Not invoiced

Lines that must never go on a customer invoice, whatever the folder says: registering the
time, fixing the setup, work on the harness done inside a customer project. Written from
the Time page; applied by `ops/time/rollup.py` when a day is finalized and by the entry
page when it groups one, so a line here is never billable however it is re-derived.

A row matches a timesheet line by Date and Project. Activity and Task narrow it when given
(`-` means any). `*` in Date means every date for that project. See ops/time/README.md 6.1.

| Date | Project | Activity | Task | Why | Recorded |
|---|---|---|---|---|---|
"""

_CELL = re.compile(r"^\|(.*)\|\s*$")


def path_for(root=None):
    return os.path.join(root or ROOT, "not-invoiced.md")


def _one(v):
    v = (v or "").strip()
    return "" if v in ("", "-") else v


def entries(root=None):
    """-> [{date, project, activity, task, why, recorded}]. Missing file gives []."""
    try:
        with io.open(path_for(root), encoding="utf-8", newline="") as f:
            text = f.read()
    except Exception:
        return []
    out = []
    for line in text.splitlines():
        m = _CELL.match(line.strip())
        if not m:
            continue
        c = [x.strip() for x in m.group(1).split("|")]
        if len(c) < 4 or c[0] == "Date" or set(c[0]) <= set("-"):
            continue
        if c[0] != "*" and not re.match(r"^\d{4}-\d{2}-\d{2}$", c[0]):
            continue
        out.append({"date": c[0], "project": c[1], "activity": _one(c[2]),
                    "task": _one(c[3]), "why": c[4] if len(c) > 4 else "",
                    "recorded": c[5] if len(c) > 5 else ""})
    return out


def covers(date, project, activity="", task="", rows=None, root=None):
    """Is this line on the register?

    A row with no Activity and no Task covers the whole project on that date -- which is
    the common case, because the decision is usually about the work, not about which F&O
    dimension it happened to land on."""
    for r in rows if rows is not None else entries(root):
        if r["project"] != project:
            continue
        if r["date"] != "*" and r["date"] != date:
            continue
        if r["activity"] and r["activity"] != (activity or ""):
            continue
        if r["task"] and r["task"] != (task or ""):
            continue
        return r
    return None


def record(date, project, activity="", task="", why="", root=None):
    """Append one decision. -> (ok, message). Idempotent: an identical row is not repeated.

    Appends, never rewrites: the register is a log of decisions and an earlier one stays
    readable even after the line it named has been moved somewhere else."""
    if date != "*" and not re.match(r"^\d{4}-\d{2}-\d{2}$", date or ""):
        return False, "bad date: %r" % (date,)
    if not re.match(r"^(Dev|customers/[^|\n]+|own/[^|\n]+)$", project or ""):
        return False, "not a project: %r" % (project,)
    if not project.startswith("customers/"):
        return False, "%s is already not invoiced" % project
    # A pipe would end the cell and a newline would end the row, so both become a space --
    # and the run of whitespace that leaves is collapsed, because the value goes into a
    # table a person reads.
    clean = lambda v: re.sub(r"\s+", " ", re.sub(r"[|\n\r]+", " ", v or "")).strip()
    activity, task, why = clean(activity), clean(task), clean(why)[:200]

    path = path_for(root)
    have = entries(root)
    if covers(date, project, activity, task, have):
        return True, "%s on %s was already marked not invoiced" % (project, date)
    row = "| %s | %s | %s | %s | %s | %s |\n" % (
        date, project, activity or "-", task or "-", why or "-",
        datetime.date.today().isoformat())
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        exists = os.path.exists(path)
        with io.open(path, "a" if exists else "w", encoding="utf-8", newline="") as f:
            if not exists:
                f.write(HEADER)
            f.write(row)
    except Exception as exc:
        return False, str(exc)
    return True, "%s on %s will never be invoiced" % (project, date)
