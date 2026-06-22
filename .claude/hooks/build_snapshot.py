#!/usr/bin/env python
"""Build the capped session-start memory snapshot (INJECTION job).

Reads ops/memory/store/*.md frontmatter and emits an ASCII-normalized, capped digest to
stdout: identity + behavioral preferences + key knowledge gists. The SessionStart hook emits
this before the workspace walk. ASCII output keeps it encoding-proof through any shell.
See C:\\Dev\\ops\\memory\\README.md (INJECTION recipe). The by-hand fallback is: read
store/MEMORY.md and the latest daily/ entry.
"""
import os, re, sys

STORE = os.environ.get("MEMORY_STORE_DIR", r"C:\Dev\ops\memory\store")
CAP_CHARS = 4000

_REPL = {
    "—": "-", "–": "-", "→": "->", "×": "x", "·": "-",
    "“": '"', "”": '"', "‘": "'", "’": "'", "…": "...",
    "≥": ">=", "≤": "<=", "≠": "!=",
}


def asciify(s):
    for k, v in _REPL.items():
        s = s.replace(k, v)
    return s.encode("ascii", "ignore").decode("ascii")


def records():
    out = []
    try:
        for fn in sorted(os.listdir(STORE)):
            if not fn.endswith(".md") or fn == "MEMORY.md":
                continue
            txt = open(os.path.join(STORE, fn), encoding="utf-8").read()
            m = re.match(r"^---\s*\n(.*?)\n---", txt, re.S)
            if not m:
                continue
            fm = m.group(1)
            rid_m = re.search(r"^id:\s*(.+)$", fm, re.M)
            rid = rid_m.group(1).strip() if rid_m else fn[:-3]
            d_m = re.search(r"^description:\s*(.+)$", fm, re.M)
            desc = d_m.group(1).strip().strip('"') if d_m else ""
            t_m = re.search(r"^tags:\s*\[(.*?)\]", fm, re.M)
            tags = [t.strip() for t in t_m.group(1).split(",")] if t_m else []
            cat = tags[0] if tags else "reference"
            out.append((cat, rid, desc))
    except Exception:
        pass
    return out


def main():
    by = {}
    for cat, rid, desc in records():
        by.setdefault(cat, []).append((rid, desc))

    lines = ["## Memory snapshot - ops/memory/store (recall: grep store/ + daily/, cite the source)"]
    for rid, desc in by.get("user", []):
        lines.append("Identity: %s" % desc)
    fb = by.get("feedback", [])
    if fb:
        lines.append("Preferences (honor these):")
        for rid, desc in fb:
            lines.append("- %s: %s" % (rid, desc))
    know = by.get("project", []) + by.get("reference", [])
    if know:
        lines.append("Knowledge:")
        for rid, desc in know:
            lines.append("- %s: %s" % (rid, desc))

    text = asciify("\n".join(lines))
    if len(text) > CAP_CHARS:
        text = text[:CAP_CHARS].rstrip() + "\n... (snapshot capped; recall for more)"
    sys.stdout.write(text + "\n")


if __name__ == "__main__":
    try:
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
        main()
    except Exception:
        pass
