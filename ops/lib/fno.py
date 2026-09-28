"""What F&O needs before a line can be entered.

A Dynamics F&O time line is **Project ID -> Activity -> Task** (ops/time/README.md sec.4).
*Which* of the three a given customer actually requires is the customer's own rule, and until
now it lived only as prose in that README's section 4.1 -- so nothing could check a line
against it. It now lives where the customer lives: the `## Customer` block of
`customers/<client>/CLAUDE.md`, beside `name` and `status`, in the same `key: value` form the
project `## Identity` block already uses for `fno_code`.

    fno_firma: Power                        the internal company that invoices this customer
    fno_code: 4058                          default Proj ID for the customer's projects
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
    CLAUDE.md carries while it waits for a code; **`none` is what a task file carries for
    "no Azure DevOps work item yet"** (the convention is id-or-`none`, never blank, so the
    absence is deliberate and visible). All of them are placeholders, and treating a
    placeholder as a value is how a `?` or a literal `none` reaches a timesheet."""
    v = (value or "").strip()
    return ((not v) or v.upper() in ("UNSET", "NONE") or v.upper().startswith("PENDING")
            or "?" in v)


def value_or_blank(v):
    """A dimension as it should be TYPED: a placeholder is nothing, not a word."""
    return "" if is_unset(v) else (v or "").strip()


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


def companies(root=None):
    """Parse `ops/TidsregInfo.xlsx` -> [{firma, kunde, key, projektnr, aktivitet, task_note}].

    The owner's own sheet, read straight from the workbook (stdlib zipfile + ElementTree,
    no openpyxl) so there is no exported copy to drift. It carries the internal company and,
    for most customers, the Proj ID and Activity -- the half of the rule that is the same
    for every project under that customer. The other half, what a line MUST carry, is on
    the customer node (see the module docstring).

    Returns [] on anything unreadable: a missing or malformed sheet must degrade to "the
    workspace knows less", never to a traceback in a per-turn hook."""
    folder = os.path.join(root or ROOT, "ops")
    path = ""
    try:
        for name in os.listdir(folder):
            if name.lower() == "tidsreginfo.xlsx":
                path = os.path.join(folder, name)
                break
    except OSError:
        return []
    if not path:
        return []
    ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    try:
        import zipfile
        import xml.etree.ElementTree as ET
        z = zipfile.ZipFile(path)
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")):
                shared.append("".join(t.text or "" for t in si.iter(ns + "t")))
        grid = []
        for row in ET.fromstring(z.read("xl/worksheets/sheet1.xml")).iter(ns + "row"):
            cells = {}
            for c in row.iter(ns + "c"):
                ref = re.match(r"([A-Z]+)", c.get("r") or "A")
                col = 0
                for ch in (ref.group(1) if ref else "A"):
                    col = col * 26 + (ord(ch) - 64)
                v = c.find(ns + "v")
                txt = ""
                if c.get("t") == "s" and v is not None:
                    idx = int(v.text)
                    txt = shared[idx] if idx < len(shared) else ""
                elif c.get("t") == "inlineStr":
                    txt = "".join(t.text or "" for t in c.iter(ns + "t"))
                elif v is not None:
                    txt = v.text or ""
                cells[col - 1] = txt.strip()
            grid.append([cells.get(i, "") for i in range(max(cells) + 1)] if cells else [])
    except Exception:
        return []

    out = []
    for row in grid[1:]:                       # row 0 is the header
        row = row + [""] * 5
        firma, kunde = row[0].strip(), row[1].strip()
        if not firma or not kunde:
            continue
        out.append({"firma": firma, "kunde": kunde, "key": norm(kunde),
                    "projektnr": row[2].strip(), "aktivitet": row[3].strip(),
                    "task_note": row[4].strip()})
    return out


def resolve_dims(ws_proj_id, ws_activity, rule, sheet_row):
    """How a line's Proj ID and Activity resolve, from the three places they can come from.

    -> {proj_id, activity, from_sheet, conflict}

    Precedence is the workspace first: the project's own `fno_code` and the task's own
    `activity:` are the specific answer, and the sheet is the customer-wide fallback. A
    placeholder on either side is not a value (`is_unset`), so it neither fills a gap nor
    disagrees with anything -- a `?` in the sheet used to read as both.

    A real disagreement is FLAGGED, never resolved: two different codes for one line is a
    question for the owner, and silently picking one is how the wrong one gets invoiced.

    One definition, because the entry page and the per-turn attribution check have to agree
    about whether a line can be typed."""
    rule = rule or {}
    sheet_row = sheet_row or {}
    xl_id = rule.get("proj_id") or sheet_row.get("projektnr") or ""
    weak, xl_weak = is_unset(ws_proj_id), is_unset(xl_id)
    return {
        "proj_id": ws_proj_id if not weak else ("" if xl_weak else xl_id),
        "activity": (value_or_blank(ws_activity) or rule.get("activity")
                     or sheet_row.get("aktivitet") or ""),
        "from_sheet": weak and not xl_weak,
        "conflict": bool(not weak and not xl_weak and xl_id != ws_proj_id),
    }


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
