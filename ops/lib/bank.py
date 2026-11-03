"""Hours already spent but not ready for invoicing: the hour bank.

Two reasons to hold hours back from F&O instead of entering them on the day they were
worked:

  LATER      the customer agreement invoices at a milestone (go-live, acceptance), or the
             owner holds a line until its F&O dimensions are settled.
  SPREAD     the work is not one customer's, or not one month's: engine work that several
             customers will use, a build to be spread across the months it serves.

A DEPOSIT moves the timesheet lines onto the `own/` project whose work it was (internal,
so not entered into F&O) and records here what they are worth and who they are for. A
WITHDRAWAL places hours from a deposit on a customer line on a later day; that line is
then entered into F&O as usual. A closed month is never touched. The reclaim ledger
(under-billed hours recovered in a later month) is the same thing and lives here too.

`ops/time/bank.md` is a register, like `absence.md`: the decisions only the owner can make.

    ## Deposits
    | Id | Opened | Holding | Hours | Work h | Weighted h | For | Terms | Basis |
    ## Withdrawals
    | Date | Deposit | Project | F&O line | Hours | Note |

`Hours` on a deposit is what may be invoiced (the F&O entry figure when it was banked);
`Work h` and `Weighted h` are the evidence. `For` is a customer, several (comma), or `-`.

Pure stdlib, ASCII-only.
"""
import io
import os
import re

__all__ = ["path_for", "deposits", "withdrawals", "balances", "placed"]

ROOT = os.environ.get("TIME_ROOT", r"C:\Dev\ops\time")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def path_for(root=None):
    return os.path.join(root or ROOT, "bank.md")


def _num(v):
    try:
        return float((v or "").replace(",", "."))
    except ValueError:
        return 0.0


def _sections(root=None):
    try:
        with io.open(path_for(root), encoding="utf-8") as f:
            text = f.read()
    except Exception:
        return {}
    out, cur = {}, None
    for line in text.splitlines():
        if line.startswith("## "):
            cur = line[3:].strip().lower()
            out[cur] = []
            continue
        if cur is None or not line.strip().startswith("|"):
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        out[cur].append(c)
    return out


def deposits(root=None):
    out = []
    for c in _sections(root).get("deposits", []):
        if len(c) < 9 or not DATE_RE.match(c[1]):
            continue
        out.append({"id": c[0], "opened": c[1], "holding": c[2], "hours": _num(c[3]),
                    "work": _num(c[4]), "weighted": _num(c[5]),
                    "for": [x.strip() for x in c[6].split(",") if x.strip() not in ("", "-")],
                    "terms": c[7], "basis": c[8]})
    return out


def withdrawals(root=None):
    out = []
    for c in _sections(root).get("withdrawals", []):
        if len(c) < 5 or not DATE_RE.match(c[0]):
            continue
        out.append({"date": c[0], "deposit": c[1], "project": c[2], "line": c[3],
                    "hours": _num(c[4]), "note": c[5] if len(c) > 5 else ""})
    return out


def balances(root=None):
    """Every deposit with what has been drawn from it and what remains."""
    drawn = {}
    for w in withdrawals(root):
        drawn[w["deposit"]] = drawn.get(w["deposit"], 0.0) + w["hours"]
    out = []
    for d in deposits(root):
        used = round(drawn.get(d["id"], 0.0), 2)
        out.append(dict(d, drawn=used, remaining=round(d["hours"] - used, 2)))
    return out


def placed(root=None):
    """Withdrawals as [{date, project, hours}]: registered on that date, not worked on it,
    so a check of billed against measured has to hold them apart."""
    return [{"date": w["date"], "project": w["project"], "hours": w["hours"]}
            for w in withdrawals(root)]
