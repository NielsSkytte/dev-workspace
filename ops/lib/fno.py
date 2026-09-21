"""What F&O needs before a line can be entered.

A Dynamics F&O time line is **Project ID -> Activity -> Task** (ops/time/README.md sec.4).
*Which* of the three a given customer actually requires is the customer's own rule, and until
now it lived only as prose in that README's section 4.1 -- so nothing could check a line
against it. It now lives where the customer lives: the `## Customer` block of
`customers/<client>/CLAUDE.md`, beside `name` and `status`, in the same `key: value` form the
project `## Identity` block already uses for `fno_code`.

    fno_firma: Power                        the internal company that invoices this customer
    fno_code: 4058-1                        default Proj ID for the customer's projects
    fno_activity: 111749                    default Activity
    fno_requires: task                      comma list: task, activity, description
    fno_billable: no                        the F&O line carries `Linjeegenskab: No charge`
    fno_description: 45394 Lineage doc      the `Beskrivelse` text, where one is required

Absent fields mean "nothing extra required", so a customer with no rule needs no block. The
README table stays as the human record of what was confirmed and when; these fields are what
the entry page reads.

Derive-only: this module reads, it never writes. The dashboard's write path edits the same
fields through the ordinary CLAUDE.md editor.
"""
import os
import re

from .substrate import read
from .workspace import ROOT, customer_dirs

# A customer is named slightly differently in the workspace folder, in the owner's
# TidsregInfo.xlsx and in prose. Normalising to a bare lowercase key is what lets the three
# meet; the aliases cover the cases normalisation cannot.
ALIASES = {
    "jtj": "joeandthejuice",
    # Typo in the source sheet: it reads "Vestforbraeding", missing the n after ae
    # (correct Danish is Vestforbraending). Aliased so the entry page works; fix the xlsx and
    # this line becomes dead.
    "vestforbraeding": "vestforbraending",
}

# The three F&O dimensions plus the one free-text field Element Logic requires. Ordered as the
# line is built, which is also the order a missing-field list reads best in.
DIMENSIONS = ("proj_id", "activity", "fno_task", "description")

_FIELD_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:(.*)$")


def norm(name):
    """A customer name from any of the three sources -> one comparable key."""
    s = (name or "").strip().lower()
    for a, b in (("æ", "ae"), ("ø", "oe"), ("å", "aa")):
        s = s.replace(a, b)
    s = re.sub(r"[\s\-_/.]", "", s)
    return ALIASES.get(s, s)


def is_unset(value):
    """True when a Proj ID / Activity / Task is present as text but says nothing.

    `UNSET` is what the rollup writes for a project with no `fno_code`; `?` and `6013-?` are
    what the owner writes in the sheet for "not assigned yet"; `PENDING...` is what a project
    CLAUDE.md carries while it waits for a code. All three are placeholders, and treating a
    placeholder as a value is how a `?` reaches a timesheet."""
    v = (value or "").strip()
    return (not v) or v.upper() == "UNSET" or v.upper().startswith("PENDING") or "?" in v


def _block(text, header):
    """The `key: value` lines of one `## Header` block -> dict. Trailing `# comment` stripped."""
    m = re.search(r"^## +%s\s*$(.*?)(?=^## |\Z)" % header, text, re.M | re.S)
    out = {}
    if not m:
        return out
    for line in m.group(1).splitlines():
        f = _FIELD_RE.match(line)
        if f:
            out[f.group(1)] = f.group(2).split("#", 1)[0].strip()
    return out


def rule_for(path):
    """One customer node CLAUDE.md -> its F&O rule, or None when the file says nothing.

    Both block names are read: a customer node writes `## Customer`, a project writes
    `## Identity`, and the customer nodes were not all written the same year."""
    text = read(path)
    if not text:
        return None
    f = _block(text, "Customer")
    f.update({k: v for k, v in _block(text, "Identity").items() if v})
    req = set(x.strip().lower() for x in (f.get("fno_requires") or "").split(",") if x.strip())
    billable = (f.get("fno_billable") or "").strip().lower()
    rule = {
        "firma": f.get("fno_firma") or "",
        "proj_id": f.get("fno_code") or "",
        "activity": f.get("fno_activity") or "",
        "description": f.get("fno_description") or "",
        "requires": sorted(req),
        # Only an explicit `no` turns billing off. An absent field must not silently make a
        # customer non-billable -- that is the direction that loses money quietly.
        "no_charge": billable in ("no", "false", "0", "no charge"),
        "path": path,
    }
    if not any((rule["firma"], rule["proj_id"], rule["activity"], rule["description"],
                rule["requires"], rule["no_charge"])):
        return None
    return rule


def rules(root=None):
    """-> {normalised customer key: rule}. A customer with no fno_* fields is absent."""
    out = {}
    for name, path in customer_dirs(root or ROOT):
        r = rule_for(os.path.join(path, "CLAUDE.md"))
        if r:
            r["customer"] = name
            out[norm(name)] = r
    return out


def missing(row, rule):
    """Which required F&O fields this entry row still cannot supply.

    -> [{field, label, why}], empty when the row is ready to type. Internal time is never
    entered in F&O, so it is never short of anything."""
    if row.get("firma") == "INTERNAL":
        return []
    out = []
    if not (row.get("firma") or "").strip():
        out.append({"field": "firma", "label": "Company",
                    "why": "the customer has no row in TidsregInfo.xlsx and no fno_firma"})
    if is_unset(row.get("proj_id")):
        out.append({"field": "proj_id", "label": "Proj ID",
                    "why": "no fno_code on the project and nothing usable in the sheet"})
    req = set((rule or {}).get("requires") or ())
    if "activity" in req and not (row.get("activity") or "").strip():
        out.append({"field": "activity", "label": "Activity",
                    "why": "this customer registers on activity"})
    if "task" in req and not (row.get("fno_task") or "").strip():
        out.append({"field": "fno_task", "label": "Task",
                    "why": "this customer registers on task -- every line needs one"})
    if "description" in req and not (row.get("description") or "").strip():
        out.append({"field": "description", "label": "Description",
                    "why": "this customer requires Beskrivelse on every line"})
    return out
