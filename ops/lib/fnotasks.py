"""What an F&O task id is called.

`CarlRData-555` is what goes on the time line, and it is all F&O needs. It is also the
least informative thing on the page: picking the right one out of ten at entry time means
knowing what each of them *is*.

Two sources, in order:

1. **`ops/time/fno-tasks.md`** -- the name as Azure DevOps has it, recorded here because
   nothing in this workspace reads DevOps. Written from the Time page the first time an id
   is used, so it is filled in as the ids are met rather than up front.
2. **the work-task that carries the id** -- `ops/tasks/<state>/<slug>.md` with
   `fno_task: <id>`, whose `title:` describes the same work from our side. Every id in use
   has at least one, so there is always something to show even before (1) exists.

The name is **display only**. What is written to a timesheet line is the id and nothing
else, because that is what registration takes; a name in the Task column would be rejected
by F&O and would be wrong in an invoice.

Pure stdlib, ASCII-only.
"""
import datetime
import io
import os
import re

__all__ = ["path_for", "names", "record", "resolve", "HEADER"]

ROOT = os.environ.get("TIME_ROOT", r"C:\Dev\ops\time")

HEADER = """# F&O task names

What each Azure DevOps work-item id is called, so the id can be picked by name at entry
time. Nothing here reaches F&O -- the time line carries the id alone. Written from the
Time page; see ops/time/README.md 4.2.

| F&O task | Name | Customer | Recorded |
|---|---|---|---|
"""

_ROW = re.compile(r"^\|(.*)\|\s*$")
# An id is what F&O accepts in the Task column: letters, digits and dashes. Anything else
# is a typo or a name that has wandered into the wrong field.
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def path_for(root=None):
    return os.path.join(root or ROOT, "fno-tasks.md")


def names(root=None):
    """-> {id: {name, customer, recorded}} from the register. Missing file gives {}.

    A later row for the same id wins, so correcting a name is another row rather than an
    edit -- the file stays append-only and the history stays readable."""
    try:
        with io.open(path_for(root), encoding="utf-8", newline="") as f:
            text = f.read()
    except Exception:
        return {}
    out = {}
    for line in text.splitlines():
        m = _ROW.match(line.strip())
        if not m:
            continue
        c = [x.strip() for x in m.group(1).split("|")]
        if len(c) < 2 or c[0] == "F&O task" or set(c[0]) <= set("-"):
            continue
        if not ID_RE.match(c[0]) or not c[1] or c[1] == "-":
            continue
        out[c[0]] = {"name": c[1], "customer": c[2] if len(c) > 2 else "",
                     "recorded": c[3] if len(c) > 3 else ""}
    return out


def record(task_id, name, customer="", root=None):
    """Append one name. -> (ok, message)."""
    task_id = (task_id or "").strip()
    if not ID_RE.match(task_id):
        return False, "not an F&O task id: %r" % (task_id,)
    clean = lambda v: re.sub(r"\s+", " ", re.sub(r"[|\n\r]+", " ", v or "")).strip()
    name, customer = clean(name)[:120], clean(customer)[:60]
    if not name:
        return False, "give it a name"
    have = names(root)
    if (have.get(task_id) or {}).get("name") == name:
        return True, "%s is already called that" % task_id

    path = path_for(root)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        exists = os.path.exists(path)
        with io.open(path, "a" if exists else "w", encoding="utf-8", newline="") as f:
            if not exists:
                f.write(HEADER)
            f.write("| %s | %s | %s | %s |\n" % (task_id, name, customer or "-",
                                                 datetime.date.today().isoformat()))
    except Exception as exc:
        return False, str(exc)
    return True, "%s: %s" % (task_id, name)


def resolve(task_ids, tasks, root=None, registered=None):
    """-> {id: {name, source, titles}} for every id given.

    `tasks` is the workspace's own task list (dicts with `fno_task` and `title`). `source`
    says which answer was used, so the page can show a registered name plainly and a
    borrowed one as what it is -- our description of the work, not DevOps' name for it."""
    reg = registered if registered is not None else names(root)
    by_id = {}
    for t in tasks or ():
        tid = (t.get("fno_task") or "").strip()
        if tid and tid not in ("none", "-"):
            by_id.setdefault(tid, []).append(t.get("title") or t.get("slug") or "")
    out = {}
    for tid in task_ids:
        titles = by_id.get(tid) or []
        if tid in reg:
            rec = {"name": reg[tid]["name"], "source": "register", "titles": titles}
        elif titles:
            rec = {"name": titles[0], "source": "work-task", "titles": titles}
        else:
            rec = {"name": "", "source": "", "titles": []}
        # Whether F&O would accept it at all. A work-task slug, or an id with a
        # parenthetical after it, has ended up in the Task column before now -- it reads
        # fine on this page and is rejected at the journal.
        rec["ok"] = bool(ID_RE.match(tid))
        out[tid] = rec
    return out
