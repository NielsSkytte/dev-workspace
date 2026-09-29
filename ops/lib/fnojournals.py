"""What is in F&O, as read back after entry (ops/time/fno-journals.md).

The Time page plans what goes into F&O; this register says what is there. One row per
journal line, written only from what F&O showed -- the line after saving, the journal
total, the approval message -- so the page can hold the plan against the fact:

    | Journal | Company | Status | Date | Customer | Proj ID | Activity | Task | Hours | Verified |

Status is Created, Finished or Posted. `-` in Activity or Task means none.

Pure stdlib, ASCII-only.
"""
import io
import os
import re

__all__ = ["path_for", "entries", "STATUSES"]

ROOT = os.environ.get("TIME_ROOT", r"C:\Dev\ops\time")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
STATUSES = ("Created", "Finished", "Posted")


def path_for(root=None):
    return os.path.join(root or ROOT, "fno-journals.md")


def _dim(v):
    return "" if v in ("", "-") else v


def entries(root=None):
    """Every row -> [{journal, company, status, date, customer, proj_id, activity, fno_task,
    hours, verified}]. A missing file gives []; a row that does not parse is skipped."""
    try:
        with io.open(path_for(root), encoding="utf-8", newline="") as f:
            text = f.read()
    except Exception:
        return []
    out = []
    for line in text.splitlines():
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) < 10 or not DATE_RE.match(c[3]) or c[2] not in STATUSES:
            continue
        try:
            hours = float(c[8])
        except ValueError:
            continue
        out.append({"journal": c[0], "company": c[1], "status": c[2], "date": c[3],
                    "customer": c[4], "proj_id": c[5], "activity": _dim(c[6]),
                    "fno_task": _dim(c[7]), "hours": hours, "verified": c[9]})
    return out
