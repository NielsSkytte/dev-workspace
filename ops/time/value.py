#!/usr/bin/env python
"""Value model: keyboard time + weighted hours per F&O line, with an audit record.

Derive-only. Reads heartbeats (attribution) and session transcripts (evidence), writes
ops/time/value/<date>.md (the audit record you show when asked to justify a charge) and
ops/time/value/<date>.jsonl (per-turn machine records). It never writes heartbeats and
never writes the timesheet -- rollup.py still owns ops/time/timesheet/.

See ops/time/README.md section 7 for the spec and the by-hand recipe, and
ops/decisions/ADR-004-value-based-billing.md for why.

PROVISIONAL CONSTANTS: the tier multipliers below are NOT evidence-based. T1-T4 are Niels's
judgement; T5 was fitted to a single completed deliverable (ElementLogic lineage engine,
2026-08-05) and is therefore exactly determined and untested. Re-evaluate when a second
deliverable completes. Everything else in this file is derived from the transcript.

Modes:
  python ops/time/value.py                 derive every complete past day not yet written
  python ops/time/value.py --preview       today's live tally; writes nothing
  python ops/time/value.py --date D        one date (rewrites it)
  python ops/time/value.py --month [M]     by-date report for a month; writes nothing
"""
import sys, os, json, glob, re, datetime, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rollup  # F&O dimension resolution + round_quarter; single-sourced on purpose

DEV_WORKSPACE = os.environ.get("DEV_WORKSPACE", r"C:\Dev")
HEARTBEATS = os.path.join(DEV_WORKSPACE, "ops", "time", "heartbeats")
VALUEDIR = os.path.join(DEV_WORKSPACE, "ops", "time", "value")
TRANSCRIPTS = os.environ.get(
    "CLAUDE_TRANSCRIPTS",
    os.path.join(os.path.expanduser("~"), ".claude", "projects"))

# ---------------------------------------------------------------- constants

IDLE_GAP = 5.0        # min. Splits stretches AND caps intra-turn dead time. One rule, both levels.
TAIL_BUFFER = 5.0     # min per stretch, unweighted
MIN_HOURS = 0.5       # per F&O line per day, as rollup.py
CUSTOMER_CAP = 9.0    # h per CUSTOMER per day -- hard, triggers spill. The only view a customer has.
FLAG_CAP = 15.0       # h across all customers -- soft, internal review flag. Never moves hours.
ABS_CAP = 24.0        # h across all customers -- theoretical
SPILL_STEP = 0.25
FALLBACK_WINDOW = 30.0  # min. A turn with no covering heartbeat may borrow attribution from
                        # the nearest one in the same session within this window; beyond it
                        # the turn is dropped rather than guessed at.

# PROVISIONAL -- see module docstring
MULTIPLIER = {1: 2.0, 2: 3.0, 3: 3.0, 4: 6.0, 5: 25.0}
TIER_NAME = {1: "T1 Junior Assistant", 2: "T2 Analyst", 3: "T3 Consultant",
             4: "T4 Senior Consultant", 5: "T5 Principal Consultant"}

# Tier gates. The file-count gate was dropped 2026-08-05: it fired twice in a month and was
# wrong both times (many small config edits are not a subsystem). Lines/newfile caught every
# genuine event on their own.
T4_MIN_LINES = 20       # weighted lines in a turn to count as "produced an artifact"
T5_LINES = 600          # weighted lines across a stretch
T5_NEWFILE = 300        # a single new file this large
ADJ_LINES = 30          # below this, on a file already credited, it is an adjustment
REBUILD_LINES = 150     # at/above this, on a credited file, it is a rebuild (re-credits)

# Deliverable classes. Knowledge is denser per line than code (Niels, 2026-08-05); workspace
# bookkeeping is not a customer deliverable. The weight scales the CHANGED-LINE COUNT, which
# feeds the tier gates and the new/revision/adjustment call -- it never scales hours directly.
CLASS_WEIGHT = [
    ("ops/memory/daily/", 0.0, "memory-raw"),      # written by the local summarizer hook
    ("ops/memory/", 0.5, "memory-curated"),
    ("ops/tasks/", 0.0, "bookkeeping"),
    ("ops/time/", 0.0, "bookkeeping"),
    ("ops/", 0.25, "workspace"),
]
KNOWLEDGE_FILES = ("context.md", "readme.md", "claude.md", "agents.md", "inbox.md")

# ---------------------------------------------------------------- tools

READ_TOOLS = set(["Read", "Grep", "Glob", "NotebookRead", "TaskGet", "TaskList",
                  "ListMcpResourcesTool", "ReadMcpResourceTool", "ReadMcpResourceDirTool"])
RESEARCH_TOOLS = set(["WebSearch", "WebFetch", "Agent", "Task", "Explore", "ToolSearch"])
MUTATE_TOOLS = set(["Write", "Edit", "MultiEdit", "NotebookEdit"])
NEUTRAL_TOOLS = set(["TodoWrite", "AskUserQuestion", "Skill", "TaskCreate", "TaskUpdate",
                     "EnterPlanMode", "ExitPlanMode", "ScheduleWakeup", "ReportFindings"])
SHELL_TOOLS = set(["Bash", "PowerShell", "BashOutput", "KillShell"])

READ_CMD = re.compile(
    r"^\s*[\(\{]?\s*(?:git\s+(?:status|log|diff|show|branch|remote|rev-parse|ls-files)"
    r"|ls|dir|pwd|cd|cat|type|head|tail|wc|find|grep|rg|echo|which|where|whoami|date|env"
    r"|Get-ChildItem|Get-Content|Get-Item|Get-Location|Test-Path|Select-String|Measure-Object"
    r"|Get-Command|Get-Process|Get-Date|Resolve-Path|Compare-Object|Select-Object|gci|gc)\b",
    re.IGNORECASE)


def is_research_tool(name):
    if name in RESEARCH_TOOLS:
        return True
    n = name.lower()
    for marker in ("docs_search", "docs_fetch", "code_sample_search", "microsoft_docs"):
        if marker in n:
            return True
    return False


# ---------------------------------------------------------------- helpers

def parse_ts(s):
    if not s:
        return None
    try:
        d = datetime.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except Exception:
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=datetime.timezone.utc)
    return d.astimezone(datetime.timezone.utc)


def nlines(s):
    if not isinstance(s, str) or not s:
        return 0
    return s.count("\n") + 1


def relpath(p):
    """Absolute path -> workspace-relative, lowercase, forward slashes. '' if outside."""
    try:
        q = os.path.abspath(p).replace("\\", "/")
    except Exception:
        return ""
    root = DEV_WORKSPACE.replace("\\", "/")
    if not q.lower().startswith(root.lower() + "/"):
        return ""
    if "/appdata/local/temp/" in q.lower():
        return ""
    return q[len(root) + 1:].lower()


def class_of(rel):
    """-> (weight, class name)"""
    for prefix, w, name in CLASS_WEIGHT:
        if rel.startswith(prefix):
            return w, name
    base = rel.rsplit("/", 1)[-1]
    if base in KNOWLEDGE_FILES or "/docs/" in rel or "/wiki/" in rel:
        return 2.0, "knowledge"
    if base.endswith(".md"):
        return 1.5, "document"
    return 1.0, "artifact"


def mutation(name, inp):
    """-> (relpath, weighted_lines, raw_lines, is_full_write, class) or None."""
    if not isinstance(inp, dict):
        return None
    rel = relpath(inp.get("file_path") or inp.get("notebook_path") or "")
    if not rel:
        return None
    if name == "Write":
        raw, full = nlines(inp.get("content")), True
    elif name == "MultiEdit" and isinstance(inp.get("edits"), list):
        raw = sum(nlines(e.get("new_string")) for e in inp["edits"] if isinstance(e, dict))
        full = False
    elif name in ("Edit", "MultiEdit"):
        raw, full = nlines(inp.get("new_string")), False
    elif name == "NotebookEdit":
        raw, full = nlines(inp.get("new_source")), False
    else:
        return None
    w, cls = class_of(rel)
    return (rel, int(round(raw * w)), raw, full, cls)


def customer_of(project):
    parts = project.split("/")
    if parts[0] == "customers" and len(parts) > 1:
        return parts[1]
    return None


# ---------------------------------------------------------------- transcripts

def is_real_user(obj):
    """A genuine user prompt -- not a tool_result carrier, not a meta line."""
    if obj.get("type") != "user" or obj.get("isMeta"):
        return False
    c = (obj.get("message") or {}).get("content")
    if isinstance(c, str):
        return bool(c.strip())
    if isinstance(c, list):
        for b in c:
            if isinstance(b, dict) and b.get("type") == "tool_result":
                return False
        for b in c:
            if isinstance(b, dict) and b.get("type") == "text" and b.get("text", "").strip():
                return True
    return False


def load_turns():
    """-> {session8: [turn]}. A turn spans one user prompt to its last production event.

    'events' holds every production timestamp so intra-turn dead time can be removed: a
    pending permission prompt or a long-running tool call is not keyboard time. Verified
    2026-08-05 on a 131-minute turn that contained 8.8 minutes of activity."""
    out = collections.defaultdict(list)
    for path in glob.glob(os.path.join(TRANSCRIPTS, "*", "*.jsonl")):
        s8 = os.path.basename(path)[:-6][:8]
        cur = None
        try:
            fh = open(path, encoding="utf-8")
        except Exception:
            continue
        with fh as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                ts = parse_ts(obj.get("timestamp"))
                if is_real_user(obj) and not obj.get("isSidechain"):
                    cur = {"start": ts, "end": ts, "events": [ts], "reads": 0,
                           "execs": 0, "research": 0, "muts": []}
                    if ts:
                        out[s8].append(cur)
                    continue
                if cur is None or ts is None:
                    continue
                c = (obj.get("message") or {}).get("content")
                produced = obj.get("type") == "assistant"
                if not produced and obj.get("type") == "user" and isinstance(c, list):
                    for b in c:
                        if isinstance(b, dict) and b.get("type") == "tool_result":
                            produced = True
                            break
                if produced:
                    cur["events"].append(ts)
                    if ts > cur["end"]:
                        cur["end"] = ts
                if not isinstance(c, list):
                    continue
                for b in c:
                    if not (isinstance(b, dict) and b.get("type") == "tool_use"):
                        continue
                    name = b.get("name") or ""
                    inp = b.get("input") or {}
                    if name in MUTATE_TOOLS:
                        m = mutation(name, inp)
                        if m:
                            cur["muts"].append(m)
                    elif name in READ_TOOLS:
                        cur["reads"] += 1
                    elif is_research_tool(name):
                        cur["research"] += 1
                    elif name in SHELL_TOOLS:
                        cmd = inp.get("command", "") if isinstance(inp, dict) else ""
                        if READ_CMD.match(cmd or ""):
                            cur["reads"] += 1
                        else:
                            cur["execs"] += 1
                    elif name in NEUTRAL_TOOLS:
                        pass
                    elif name.startswith("mcp__"):
                        cur["execs"] += 1
    for k in out:
        out[k].sort(key=lambda t: t["start"])
    return out


def load_heartbeats():
    out = collections.defaultdict(list)
    for path in sorted(glob.glob(os.path.join(HEARTBEATS, "*.jsonl"))):
        try:
            fh = open(path, encoding="utf-8")
        except Exception:
            continue
        with fh as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    o = json.loads(line)
                    s, e = parse_ts(o["ts_start"]), parse_ts(o["ts_end"])
                except Exception:
                    continue
                if not s or not e:
                    continue
                if e < s:
                    e = s
                out[(o.get("session") or "")[:8]].append(
                    {"start": s, "end": e, "project": o.get("project") or "Dev",
                     "task": o.get("task")})
    return out


def active_minutes(events, lo, hi):
    """Sum inter-event intervals inside a turn, each capped at IDLE_GAP. Dead time drops out."""
    ev = sorted(t for t in events if t and lo <= t <= hi)
    total = 0.0
    for a, b in zip(ev, ev[1:]):
        total += min((b - a).total_seconds() / 60.0, IDLE_GAP)
    return total


def build_turns():
    """Join transcript turns to heartbeats. Heartbeats give attribution; transcripts give
    duration and evidence. Each turn is bounded by BOTH: the transcript ends a turn whose
    Stop hook never fired, the heartbeat bounds a turn whose segmentation broke on a
    resumed session."""
    hb = load_heartbeats()
    rows = []
    for s8, turns in load_turns().items():
        beats = hb.get(s8, [])
        for t in turns:
            best, overlap = None, -1
            for h in beats:
                if h["end"] < t["start"] or h["start"] > t["end"]:
                    continue
                ov = (min(h["end"], t["end"]) - max(h["start"], t["start"])).total_seconds()
                if ov > overlap:
                    best, overlap = h, ov
            attribution = "heartbeat"
            if best is None:
                # No heartbeat covers this turn -- the Stop hook is fail-silent, so its
                # heartbeat can simply be missing. Fall back to the nearest heartbeat in the
                # SAME session (same cwd, so almost always the same project), but only within
                # FALLBACK_WINDOW. Beyond that the guess is not defensible and the turn is
                # dropped. 5.5% of turns took this path over 2026-05 to 2026-08.
                if not beats:
                    continue
                best = min(beats, key=lambda x: abs((x["start"] - t["start"]).total_seconds()))
                delta = abs((best["start"] - t["start"]).total_seconds()) / 60.0
                if delta > FALLBACK_WINDOW:
                    continue
                attribution = "fallback"
                lo, hi = t["start"], t["end"]
            else:
                lo = max(t["start"], best["start"])
                hi = min(t["end"], best["end"])
                if hi < lo:
                    hi = lo
            rows.append({
                "start": lo, "end": hi,
                "kb": active_minutes(t["events"], lo, hi),
                "date": lo.astimezone().strftime("%Y-%m-%d"),
                "project": best["project"], "task": best["task"],
                "attribution": attribution,
                "reads": t["reads"], "execs": t["execs"], "research": t["research"],
                "muts": t["muts"],
            })
    rows.sort(key=lambda r: r["start"])
    return rows


# ---------------------------------------------------------------- tiering

def turn_tier(r):
    """Tier from tool evidence alone, before the ledger and the T5 stretch gate."""
    lines = sum(m[1] for m in r["muts"])
    if r["muts"]:
        return 4 if lines >= T4_MIN_LINES else 3
    if r["execs"]:
        return 3
    if r["research"] or r["reads"] >= 3:
        return 2
    return 1


def stretch_groups(items):
    """Split turns into stretches on an IDLE_GAP boundary. Returns lists of indices."""
    if not items:
        return []
    order = sorted(range(len(items)), key=lambda i: items[i]["start"])
    groups = [[order[0]]]
    end = items[order[0]]["end"]
    for i in order[1:]:
        if (items[i]["start"] - end).total_seconds() / 60.0 <= IDLE_GAP:
            groups[-1].append(i)
            if items[i]["end"] > end:
                end = items[i]["end"]
        else:
            groups.append([i])
            end = items[i]["end"]
    return groups


def score(rows):
    """Walk every turn in chronological order, maintaining the deliverable ledger.

    The ledger is rebuilt from scratch on every run -- deterministic, and no persisted state
    can drift out of sync with the heartbeats. Returns (records, ledger)."""
    ledger = {}
    byday = collections.defaultdict(list)
    for r in rows:
        byday[r["date"]].append(r)
    records = []
    for date in sorted(byday):
        groups = collections.defaultdict(list)
        for r in byday[date]:
            groups[(r["project"], r["task"])].append(r)
        for key in sorted(groups, key=lambda k: (k[0], k[1] or "")):
            project, task = key
            items = groups[key]
            rec = {"date": date, "project": project, "task": task,
                   "keyboard_min": 0.0, "turns": 0, "stretches": 0, "overhead_min": 0.0,
                   "tiers": collections.defaultdict(lambda: [0, 0.0]),
                   "deliverables": [], "t5_events": 0, "weighted_h": 0.0,
                   "fallback_turns": 0}
            weighted_min = 0.0
            for g in stretch_groups(items):
                idx = sorted(g, key=lambda i: items[i]["start"])
                rec["stretches"] += 1
                total_lines, max_new = 0, 0
                for i in idx:
                    for rel, wl, raw, full, cls in items[i]["muts"]:
                        total_lines += wl
                        if full and rel not in ledger and wl > max_new:
                            max_new = wl
                is_t5 = (total_lines >= T5_LINES or max_new >= T5_NEWFILE)
                promoted = False
                for i in idx:
                    r = items[i]
                    dur = r["kb"]
                    rec["keyboard_min"] += dur
                    rec["turns"] += 1
                    if r.get("attribution") == "fallback":
                        rec["fallback_turns"] += 1
                    tier = turn_tier(r)
                    if r["muts"]:
                        kinds = []
                        for rel, wl, raw, full, cls in r["muts"]:
                            if rel not in ledger:
                                kind = "new"
                            elif wl >= REBUILD_LINES:
                                kind = "rebuild"
                            elif wl >= ADJ_LINES:
                                kind = "revision"
                            else:
                                kind = "adjustment"
                            kinds.append((rel, wl, raw, kind, cls))
                        substantive = False
                        for k in kinds:
                            if k[3] != "adjustment":
                                substantive = True
                        if not substantive:
                            tier = max(1, tier - 1)
                        elif is_t5 and tier == 4:
                            tier = 5
                            promoted = True
                        for rel, wl, raw, kind, cls in kinds:
                            if rel not in ledger:
                                ledger[rel] = {"first": date, "tier": tier, "project": project}
                            rec["deliverables"].append(
                                {"path": rel, "raw": raw, "weighted": wl,
                                 "kind": kind, "class": cls})
                    rec["tiers"][tier][0] += 1
                    rec["tiers"][tier][1] += dur
                    weighted_min += dur * MULTIPLIER[tier]
                for a, b in zip(idx, idx[1:]):
                    gap = (items[b]["start"] - items[a]["end"]).total_seconds() / 60.0
                    gap = max(0.0, min(gap, IDLE_GAP))
                    weighted_min += gap
                    rec["overhead_min"] += gap
                weighted_min += TAIL_BUFFER
                rec["overhead_min"] += TAIL_BUFFER
                if promoted:
                    rec["t5_events"] += 1
            rec["weighted_h"] = max(rollup.round_quarter(weighted_min / 60.0), MIN_HOURS)
            rec["keyboard_h"] = rec["keyboard_min"] / 60.0
            rec["proj_id"] = rollup.project_id(project)
            activity, fno_task = rollup.task_dims(task)
            rec["activity"], rec["fno_task"] = activity, fno_task
            rec["billable"] = project.startswith("customers/")
            records.append(rec)
    return records, ledger


# ---------------------------------------------------------------- caps

def apply_caps(records):
    """Spill above-cap hours to other days. Scoped per CUSTOMER (the only view a customer
    has), never across a month boundary (a closed month may already be invoiced), distance
    before preference. Hours are preserved exactly; only dates move."""
    billable = [r for r in records if r["billable"]]
    dates = sorted(set(r["date"] for r in billable))
    moves, unplaced = [], []

    def cust_day():
        t = collections.defaultdict(float)
        for r in billable:
            t[(customer_of(r["project"]), r["date"])] += r["weighted_h"]
        return t

    guard = 0
    while guard < 2000:
        guard += 1
        cd = cust_day()
        over = [(k, v) for k, v in cd.items() if v > CUSTOMER_CAP + 1e-9]
        if not over:
            break
        (cust, date), total = max(over, key=lambda kv: kv[1])
        excess = total - CUSTOMER_CAP
        pool = [r for r in billable if r["date"] == date
                and customer_of(r["project"]) == cust and r["weighted_h"] >= SPILL_STEP]
        if not pool:
            break
        src = max(pool, key=lambda r: r["weighted_h"])
        worked = set(r["date"] for r in billable
                     if r["project"] == src["project"] and r["date"] != date)
        targets = [d for d in dates
                   if d != date and d[:7] == date[:7]
                   and cd.get((cust, d), 0.0) < CUSTOMER_CAP - 1e-9]
        if not targets:
            unplaced.append({"date": date, "project": src["project"],
                             "hours": round(excess, 2)})
            break
        here = datetime.date.fromisoformat(date)
        wk = here.isocalendar()[1]

        def rank(d):
            other = datetime.date.fromisoformat(d)
            delta = (other - here).days
            return (0 if other.isocalendar()[1] == wk else 1, abs(delta),
                    0 if delta > 0 else 1, 0 if d in worked else 1)
        targets.sort(key=rank)
        tgt = targets[0]
        room = CUSTOMER_CAP - cd.get((cust, tgt), 0.0)
        amount = min(SPILL_STEP, excess, src["weighted_h"], room)
        amount = round(amount / SPILL_STEP) * SPILL_STEP
        if amount < SPILL_STEP:
            unplaced.append({"date": date, "project": src["project"],
                             "hours": round(excess, 2)})
            break
        src["weighted_h"] = round(src["weighted_h"] - amount, 2)
        hit = None
        for r in billable:
            if r["date"] == tgt and r["project"] == src["project"] and r["task"] == src["task"]:
                hit = r
                break
        if hit:
            hit["weighted_h"] = round(hit["weighted_h"] + amount, 2)
        else:
            clone = {"date": tgt, "project": src["project"], "task": src["task"],
                     "keyboard_min": 0.0, "keyboard_h": 0.0, "turns": 0, "stretches": 0,
                     "overhead_min": 0.0, "tiers": {}, "deliverables": [], "t5_events": 0,
                     "weighted_h": amount, "proj_id": src["proj_id"],
                     "activity": src["activity"], "fno_task": src["fno_task"],
                     "billable": True, "spilled_from": date}
            billable.append(clone)
            records.append(clone)
        moves.append({"from": date, "to": tgt, "project": src["project"],
                      "hours": amount})
    records[:] = [r for r in records if r["weighted_h"] >= 0.01]

    day_total = collections.defaultdict(float)
    for r in records:
        if r["billable"]:
            day_total[r["date"]] += r["weighted_h"]
    flags = []
    for d in sorted(day_total):
        if day_total[d] > ABS_CAP:
            flags.append({"date": d, "hours": round(day_total[d], 2), "level": "IMPOSSIBLE"})
        elif day_total[d] > FLAG_CAP:
            flags.append({"date": d, "hours": round(day_total[d], 2), "level": "REVIEW"})
    return moves, unplaced, flags


# ---------------------------------------------------------------- rendering

def render_day(date, records, moves, flags):
    day = [r for r in records if r["date"] == date]
    day.sort(key=lambda r: (not r["billable"], r["project"], r["activity"], r["fno_task"]))
    out = []
    out.append("# Value record - %s (%s)" % (
        date, datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%a")))
    out.append("")
    out.append("Derived by ops/time/value.py from heartbeats + session transcripts.")
    out.append("Keyboard time is measured; weighted hours apply PROVISIONAL tier multipliers")
    out.append("(see ADR-004). This record is the justification for the charge - it is not")
    out.append("the timesheet. Corrections go in the timesheet, never here.")
    out.append("")
    out.append("| Project | Proj ID | Activity | Task | Keyboard h | Weighted h | Billable |")
    out.append("|---|---|---|---|---|---|---|")
    kb_b = w_b = kb_i = w_i = 0.0
    for r in day:
        out.append("| %s | %s | %s | %s | %.2f | %.2f | %s |" % (
            r["project"], r["proj_id"], r["activity"] or "-", r["fno_task"] or "-",
            r["keyboard_h"], r["weighted_h"], "yes" if r["billable"] else "no"))
        if r["billable"]:
            kb_b += r["keyboard_h"]; w_b += r["weighted_h"]
        else:
            kb_i += r["keyboard_h"]; w_i += r["weighted_h"]
    out.append("")
    out.append("**Billable:** %.2f h keyboard -> %.2f h weighted" % (kb_b, w_b))
    out.append("**Internal:** %.2f h keyboard -> %.2f h weighted" % (kb_i, w_i))
    for f in flags:
        if f["date"] == date:
            out.append("")
            out.append("> **%s** - %.2f weighted h across all customers this day. These are"
                       % (f["level"], f["hours"]))
            out.append("> WEIGHTED hours, not clock hours; check the classifier before the invoice.")
    agg_moves = collections.defaultdict(float)
    for m in moves:
        if m["from"] == date or m["to"] == date:
            agg_moves[(m["from"], m["to"], m["project"])] += m["hours"]
    if agg_moves:
        out.append("")
        out.append("Cap spill (%.1f h per customer per day):" % CUSTOMER_CAP)
        for k in sorted(agg_moves):
            frm, to, proj = k
            out.append("  - %s: %s -> %s, %.2f h" % (proj, frm, to, agg_moves[k]))
    out.append("")
    out.append("---")
    for r in day:
        if not r["turns"]:
            continue
        out.append("")
        out.append("## %s  [task: %s]" % (r["project"], r["task"] or "-"))
        out.append("")
        hh = int(r["keyboard_min"]) // 60
        mm = int(round(r["keyboard_min"])) % 60
        out.append("Keyboard time : %dh %02dm across %d turns in %d stretches"
                   % (hh, mm, r["turns"], r["stretches"]))
        out.append("Weighted      : %.2f h" % r["weighted_h"])
        if r["keyboard_min"] > 0:
            out.append("Effective     : %.1fx" % (r["weighted_h"] * 60 / r["keyboard_min"]))
        if r.get("fallback_turns"):
            out.append("Attribution   : %d of %d turns had no covering heartbeat and borrowed"
                       % (r["fallback_turns"], r["turns"]))
            out.append("                the project from the nearest one in the same session.")
        out.append("")
        out.append("| Tier | Turns | Keyboard min | Multiplier | Weighted h |")
        out.append("|---|---|---|---|---|")
        for t in sorted(r["tiers"]):
            n, mins = r["tiers"][t]
            out.append("| %s | %d | %.0f | %.1fx | %.2f |"
                       % (TIER_NAME[t], n, mins, MULTIPLIER[t], mins * MULTIPLIER[t] / 60))
        out.append("| *gap + tail* | - | %.0f | 1.0x | %.2f |"
                   % (r["overhead_min"], r["overhead_min"] / 60))
        if r["deliverables"]:
            agg = {}
            for d in r["deliverables"]:
                k = (d["path"], d["kind"], d["class"])
                cell = agg.setdefault(k, [0, 0])
                cell[0] += d["raw"]; cell[1] += d["weighted"]
            out.append("")
            out.append("Deliverables touched:")
            out.append("")
            out.append("| File | Raw lines | Weighted | Kind | Class |")
            out.append("|---|---|---|---|---|")
            for k in sorted(agg, key=lambda x: -agg[x][1]):
                path, kind, cls = k
                raw, w = agg[k]
                out.append("| %s | %d | %d | %s | %s |" % (path, raw, w, kind, cls))
        if r["t5_events"]:
            out.append("")
            out.append("**%d T5 event(s)** - a subsystem was built in this stretch, not just an"
                       % r["t5_events"])
            out.append("artifact. This is where the multiplier is largest and least tested.")
    return "\n".join(out) + "\n"


def write_day(date, records, moves, flags):
    if not os.path.isdir(VALUEDIR):
        os.makedirs(VALUEDIR)
    with open(os.path.join(VALUEDIR, date + ".md"), "w", encoding="utf-8") as f:
        f.write(render_day(date, records, moves, flags))
    with open(os.path.join(VALUEDIR, date + ".jsonl"), "w", encoding="utf-8") as f:
        for r in records:
            if r["date"] != date:
                continue
            f.write(json.dumps({
                "date": r["date"], "project": r["project"], "task": r["task"],
                "proj_id": r["proj_id"], "activity": r["activity"], "fno_task": r["fno_task"],
                "billable": r["billable"], "keyboard_h": round(r["keyboard_h"], 3),
                "weighted_h": r["weighted_h"], "turns": r["turns"],
                "stretches": r["stretches"], "t5_events": r["t5_events"],
                "fallback_turns": r.get("fallback_turns", 0),
                "tiers": dict((str(k), {"turns": v[0], "minutes": round(v[1], 2)})
                              for k, v in r["tiers"].items()),
                "deliverables": r["deliverables"],
                "spilled_from": r.get("spilled_from"),
            }, sort_keys=True) + "\n")


def summarise(records, label):
    lines = ["%-42s %10s %10s %8s" % (label, "keyboard", "weighted", "factor")]
    lines.append("-" * 74)
    agg = collections.defaultdict(lambda: [0.0, 0.0])
    for r in records:
        if not r["billable"]:
            continue
        c = customer_of(r["project"]) or r["project"]
        agg[c][0] += r["keyboard_h"]; agg[c][1] += r["weighted_h"]
    tk = tw = 0.0
    for c in sorted(agg, key=lambda k: -agg[k][1]):
        kb, w = agg[c]
        tk += kb; tw += w
        lines.append("%-42s %10.2f %10.2f %7.2fx" % (c, kb, w, (w / kb) if kb else 0))
    lines.append("-" * 74)
    lines.append("%-42s %10.2f %10.2f %7.2fx" % ("BILLABLE TOTAL", tk, tw, (tw / tk) if tk else 0))
    ik = iw = 0.0
    for r in records:
        if not r["billable"]:
            ik += r["keyboard_h"]; iw += r["weighted_h"]
    lines.append("%-42s %10.2f %10.2f" % ("(internal Dev / own)", ik, iw))
    return "\n".join(lines)


# ---------------------------------------------------------------- main

def main(argv):
    mode = "derive"
    arg = None
    if len(argv) > 1:
        if argv[1] == "--preview":
            mode = "preview"
        elif argv[1] == "--date" and len(argv) > 2:
            mode, arg = "date", argv[2]
        elif argv[1] == "--month":
            mode = "month"
            arg = argv[2] if len(argv) > 2 else datetime.date.today().strftime("%Y-%m")
        elif argv[1] in ("-h", "--help"):
            print(__doc__)
            return 0

    if not os.path.isdir(TRANSCRIPTS):
        sys.stderr.write("value.py: no transcripts at %s -- cannot derive evidence.\n"
                         % TRANSCRIPTS)
        return 2

    rows = build_turns()
    if not rows:
        print("value.py: no turns found.")
        return 0
    records, ledger = score(rows)
    moves, unplaced, flags = apply_caps(records)

    today = datetime.date.today().strftime("%Y-%m-%d")
    have = set(os.path.basename(p)[:-3]
               for p in glob.glob(os.path.join(VALUEDIR, "*.md")))
    all_dates = sorted(set(r["date"] for r in records))

    if mode == "preview":
        sel = [r for r in records if r["date"] == today]
        print(summarise(sel, "TODAY %s (preview, nothing written)" % today))
        return 0
    if mode == "month":
        sel = [r for r in records if r["date"].startswith(arg)]
        print(summarise(sel, "MONTH %s (report, nothing written)" % arg))
        return 0
    if mode == "date":
        write_day(arg, records, moves, flags)
        print(summarise([r for r in records if r["date"] == arg], "DATE %s (written)" % arg))
        return 0

    todo = [d for d in all_dates if d < today and d not in have]
    if not todo:
        print("value.py: nothing to derive (all complete days already written).")
    for d in todo:
        write_day(d, records, moves, flags)
    if todo:
        print("value.py: wrote %d day(s): %s" % (len(todo), ", ".join(todo)))
        sel = [r for r in records if r["date"] in todo]
        print()
        print(summarise(sel, "DERIVED"))
    if flags:
        print()
        for f in flags:
            print("  %s %s: %.2f weighted h across all customers (weighted, not clock)"
                  % (f["level"], f["date"], f["hours"]))
    if unplaced:
        print()
        for u in unplaced:
            print("  UNPLACED %s %s %.2f h - no day in the month had room under the %.1f h "
                  "customer cap" % (u["date"], u["project"], u["hours"], CUSTOMER_CAP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
