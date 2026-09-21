"""Reading the workspace substrate: markdown files with YAML frontmatter.

The substrate is the format -- `## Heading` sections, `- ` bullets, `**Label:** value`
lines, an Identity block, a frontmatter block. Before this module every consumer
(`dashboard.py`, `bin/daybrief.py`, `time/rollup.py`, `time/value.py`) carried its own
copy of the parsers, so a format change meant three or four edits and a missed one
failed silently.

Read-only and derive-only: nothing here writes, and nothing here holds state. Pure
stdlib, ASCII-only.

Where two readers of the same convention differ on purpose, both are here and the
difference is named -- `plain` vs `clean`, `bullets` vs `bullets_joined`, `sections`
vs `section`. That is the point: the difference is now visible in one file instead of
being spread across four.
"""
import datetime
import re

__all__ = ["read", "frontmatter", "identity", "file_field", "sections", "section",
           "bullets", "bullets_joined", "field", "labelled", "plain", "clean",
           "first_para", "first_sentence", "parse_date", "days_ago"]


# ---------- files ----------

def read(path):
    """File contents with line endings normalised, or '' if it cannot be read.

    Missing is not an error here: half the substrate is optional (a project with no
    CONTEXT.md, a task with no Log section), and every caller treats absent as empty."""
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().replace("\r\n", "\n")
    except Exception:
        return ""


def file_field(path, name, lower=True):
    """The first `name: value` line anywhere in a file, or None.

    Not frontmatter-scoped on purpose: the F&O dimension lookup reads `fno_code` out of
    a project CLAUDE.md, where it sits in the Identity block rather than in frontmatter.
    Trailing `# comment` is stripped; an empty value reads as None."""
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                probe = line.strip()
                if lower:
                    probe = probe.lower()
                if probe.startswith(name + ":"):
                    return line.split(":", 1)[1].strip().split("#", 1)[0].strip() or None
    except Exception:
        pass
    return None


# ---------- frontmatter and the Identity block ----------

_FM_RE = re.compile(r"^---[ \t]*\n(.*?\n)---[ \t]*\n", re.S)
_KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):(.*)$")


def frontmatter(text):
    """-> ({key: value}, body). No frontmatter gives ({}, text).

    Keys are matched at column 0 only, so an indented line inside a block value is
    content, not a field. Values are stripped of a trailing `# comment`."""
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    out = {}
    for line in m.group(1).splitlines():
        k = _KEY_RE.match(line)
        if k:
            out[k.group(1)] = k.group(2).split("#", 1)[0].strip()
    return out, text[m.end():]


def identity(text):
    """The `## Identity` block of a project CLAUDE.md -> {key: value}.

    A CLAUDE.md without one declares a non-project (a wiki mirror, a bootstrap stub),
    so an empty dict is a meaningful answer, not a parse failure."""
    out = {}
    block = re.search(r"^## Identity\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not block:
        return out
    for line in block.group(1).splitlines():
        m = _KEY_RE.match(line.strip())
        if m:
            out[m.group(1)] = m.group(2).split("#", 1)[0].strip()
    return out


# ---------- sections ----------

def sections(text):
    """-> {heading: body} for every `## Heading`, bodies stripped.

    Use when a caller wants several sections out of one file; `section` is the
    single-lookup form and tolerates trailing text after the heading."""
    out, cur, buf = {}, None, []
    for line in text.splitlines():
        m = re.match(r"^## +(.+?)\s*$", line)
        if m:
            if cur:
                out[cur] = "\n".join(buf).strip()
            cur, buf = m.group(1), []
        elif cur:
            buf.append(line)
    if cur:
        out[cur] = "\n".join(buf).strip()
    return out


def section(text, header_re):
    """Body of the first h2 whose heading matches `header_re`, unstripped, or ''.

    The heading may carry trailing text the pattern does not cover -- resume cards
    write `## Where we stand - 2026-09-21`, matched by `Where we stand`."""
    m = re.search(r"^## (%s)[^\n]*\n(.*?)(?=^## |\Z)" % header_re, text, re.S | re.M)
    return m.group(2) if m else ""


# ---------- list items ----------

_ITEM_RE = re.compile(r"^(?:[-*]|\d+\.)\s+(.*)$")


def bullets(body, limit=6):
    """List items of a section body as plain text, struck-through items dropped.

    `~~item~~` means resolved, so it is not an open item. `limit=None` returns all."""
    out = []
    for line in (body or "").splitlines():
        m = _ITEM_RE.match(line.strip())
        if m:
            item = m.group(1).strip()
            if item.startswith("~~"):
                continue
            out.append(plain(item))
    return out if limit is None else out[:limit]


def bullets_joined(text):
    """List items with wrapped continuation lines folded back onto their item.

    The day brief renders one line per item, so a bullet that wraps in the source file
    has to come back as one string. Indentation decides: a continuation is indented, a
    blank line ends the item. Struck-through items are NOT dropped here -- the brief
    counts what a card contains, including what has been resolved."""
    items, cur = [], None
    for line in (text or "").split("\n"):
        if re.match(r"^\s{0,1}(-|\d+\.)\s+", line):
            if cur is not None:
                items.append(cur)
            cur = re.sub(r"^\s{0,1}(-|\d+\.)\s+", "", line)
        elif cur is not None and line.startswith("  ") and line.strip():
            cur += " " + line.strip()
        elif cur is not None and not line.strip():
            items.append(cur)
            cur = None
    if cur is not None:
        items.append(cur)
    return [clean(i) for i in items if clean(i)]


# ---------- labelled lines ----------

def field(body, label):
    """The value of a `**Label:** value` line, or ''."""
    m = re.search(r"^\*\*" + re.escape(label) + r":\*\*\s*(.+)$", body or "", re.M)
    return plain(m.group(1)) if m else ""


def labelled(body, label):
    """Bullets that follow a `**Label:**` line, up to the next bold label.

    A `## State` block is written as several labelled groups in one section, so the
    label is the only boundary there is."""
    if not body:
        return []
    out, grabbing = [], False
    for line in body.splitlines():
        s = line.strip()
        if re.match(r"^\*\*.+?:\*\*", s):
            grabbing = s.lower().startswith("**" + label.lower())
            rest = re.sub(r"^\*\*.+?:\*\*", "", s).strip()
            if grabbing and rest:
                out.append(plain(rest))
            continue
        if grabbing:
            m = _ITEM_RE.match(s)
            if m:
                out.append(plain(m.group(1)))
    return out[:6]


# ---------- text normalisation ----------

def plain(s):
    """Strip inline markdown, keep the words and the line breaks.

    For text going into a web page, where the layout survives."""
    s = re.sub(r"`([^`]*)`", r"\1", s)
    s = re.sub(r"\*\*([^*]*)\*\*", r"\1", s)
    s = re.sub(r"~~([^~]*)~~", r"\1", s)
    s = re.sub(r"\[\[([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    return s.strip()


def clean(s, n=None):
    """Strip markdown and collapse all whitespace to single spaces, optionally truncated.

    For text going into a fixed-width terminal line, where a newline would break the
    layout. `plain` is the web form of the same idea."""
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"\*\*|__|`", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    if n and len(s) > n:
        s = s[:n - 3].rstrip() + "..."
    return s


def first_para(body, limit=420):
    """The first real paragraph of a section, as one line, truncated with an ellipsis."""
    for para in (body or "").split("\n\n"):
        p = plain(" ".join(x.strip() for x in para.splitlines()).strip())
        if p and not p.startswith("---"):
            return p[:limit] + ("..." if len(p) > limit else "")
    return ""


def first_sentence(s, n=220):
    """The first sentence of a passage, truncated with an ellipsis."""
    s = clean(s)
    m = re.match(r"(.+?[.!?])(\s|$)", s)
    out = m.group(1) if m else s
    return out if len(out) <= n else out[:n - 3].rstrip() + "..."


# ---------- dates ----------

def parse_date(s):
    """Leading ISO date of a string -> date, or None. Never raises."""
    try:
        return datetime.date.fromisoformat(str(s).strip()[:10])
    except Exception:
        return None


def days_ago(date_str, today):
    """Whole days between an ISO date and `today` (ISO string or date), or None."""
    d = parse_date(date_str)
    if d is None:
        return None
    ref = today if isinstance(today, datetime.date) else parse_date(today)
    if ref is None:
        return None
    return (ref - d).days
